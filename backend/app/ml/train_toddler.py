"""Q-CHAT küçük çocuk (18-24 ay) tarama modeli: nested CV ile model karşılaştırma ve eğitim.

Değerlendirilen şey tek bir model değil, tüm prosedürdür: 25 maddeden 10'unun
seçimi ve hiperparametre araması her dış fold'un yalnızca eğitim kısmında yapılır.
Böylece raporlanan metrikler, seçimin test verisini görmesinden kaynaklanan
iyimserliği taşımaz.

Çalıştırma (backend/ dizininden):
    python -m app.ml.train_toddler
"""

import json
import time
from datetime import date
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
import xgboost
from sklearn.base import clone
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import RFE
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score, roc_curve
from sklearn.model_selection import GridSearchCV, RepeatedStratifiedKFold, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from xgboost import XGBClassifier

from app.ml.qchat_items import ITEMS, SHORT_LABELS, column

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data" / "qchat_toddler_poland.csv"
MODEL_PATH = ROOT / "app" / "ml" / "artifacts" / "toddler_model.pkl"
META_PATH = ROOT / "app" / "ml" / "artifacts" / "toddler_model_meta.json"

ALL_ITEMS = list(ITEMS)
ALL_FEATURES = [column(i) for i in ALL_ITEMS]
TARGET = "asd"
N_ITEMS = 10
TARGET_SENSITIVITY = 0.90
SEED = 42

OUTER = RepeatedStratifiedKFold(n_splits=5, n_repeats=5, random_state=SEED)
INNER = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)


def _pipeline(clf, select: bool = True) -> Pipeline:
    steps = [("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]
    if select:
        steps.append(("select", RFE(LogisticRegression(max_iter=2000), n_features_to_select=N_ITEMS)))
    steps.append(("clf", clf))
    return Pipeline(steps)


# Basitten karmaşığa sıralı; model seçiminde "tek standart hata" kuralı bu sırayı kullanır.
CANDIDATES: dict[str, tuple[str, Pipeline, dict]] = {
    "logreg": (
        "Lojistik regresyon",
        _pipeline(LogisticRegression(max_iter=2000)),
        {"clf__C": [0.01, 0.1, 1.0, 10.0]},
    ),
    "svm": (
        "SVM (RBF çekirdek)",
        _pipeline(CalibratedClassifierCV(SVC(random_state=SEED), ensemble=False)),
        {"clf__estimator__C": [0.1, 1.0, 10.0], "clf__estimator__gamma": ["scale", 0.01]},
    ),
    "rf": (
        "Random Forest",
        _pipeline(RandomForestClassifier(n_estimators=200, class_weight="balanced", random_state=SEED)),
        {"clf__max_depth": [3, 5, None], "clf__min_samples_leaf": [1, 3, 5]},
    ),
    "xgb": (
        "XGBoost",
        _pipeline(XGBClassifier(eval_metric="logloss", random_state=SEED, n_jobs=1)),
        {"clf__max_depth": [2, 3], "clf__learning_rate": [0.05, 0.1], "clf__n_estimators": [100, 300]},
    ),
}

# Kısa formun maliyetini göstermek için: aynı model, 25 maddenin tamamıyla.
REFERENCE = (
    "logreg_25",
    "Lojistik regresyon (25 madde, referans)",
    _pipeline(LogisticRegression(max_iter=2000), select=False),
    {"clf__C": [0.01, 0.1, 1.0, 10.0]},
)


def _sens_spec(y: np.ndarray, proba: np.ndarray, threshold: float) -> tuple[float, float]:
    pred = proba >= threshold
    sens = (pred & (y == 1)).sum() / max((y == 1).sum(), 1)
    spec = (~pred & (y == 0)).sum() / max((y == 0).sum(), 1)
    return float(sens), float(spec)


def _summary(values: list[float]) -> dict:
    arr = np.asarray(values)
    return {"mean": round(float(arr.mean()), 4), "std": round(float(arr.std(ddof=1)), 4)}


def _bootstrap_auc_ci(y: np.ndarray, proba: np.ndarray, n: int = 2000) -> list[float]:
    rng = np.random.default_rng(SEED)
    aucs = []
    for _ in range(n):
        idx = rng.integers(0, len(y), len(y))
        if len(np.unique(y[idx])) == 2:
            aucs.append(roc_auc_score(y[idx], proba[idx]))
    return [round(float(np.percentile(aucs, 2.5)), 4), round(float(np.percentile(aucs, 97.5)), 4)]


def nested_cv(X: pd.DataFrame, y: np.ndarray, estimator: Pipeline, grid: dict) -> dict:
    fold = {"auc": [], "brier": [], "sensitivity": [], "specificity": []}
    oof_sum = np.zeros(len(y))
    oof_count = np.zeros(len(y))
    selection_counts = pd.Series(0, index=X.columns)
    chosen_params = []

    for train_idx, test_idx in OUTER.split(X, y):
        search = GridSearchCV(clone(estimator), grid, cv=INNER, scoring="roc_auc", n_jobs=-1)
        search.fit(X.iloc[train_idx], y[train_idx])

        proba = search.predict_proba(X.iloc[test_idx])[:, 1]
        y_test = y[test_idx]
        sens, spec = _sens_spec(y_test, proba, 0.5)
        fold["auc"].append(roc_auc_score(y_test, proba))
        fold["brier"].append(brier_score_loss(y_test, proba))
        fold["sensitivity"].append(sens)
        fold["specificity"].append(spec)

        oof_sum[test_idx] += proba
        oof_count[test_idx] += 1
        chosen_params.append(search.best_params_)

        selector = search.best_estimator_.named_steps.get("select")
        if selector is not None:
            selection_counts[X.columns[selector.support_]] += 1

    return {
        "fold_metrics": fold,
        "oof_proba": oof_sum / oof_count,
        "selection_frequency": (selection_counts / OUTER.get_n_splits()).round(3),
        "chosen_params": chosen_params,
    }


def _baseline(X: pd.DataFrame, y: np.ndarray) -> dict:
    """Klasik klinik yaklaşım: 25 maddenin toplam skoru (öğrenme yok)."""
    total = X.fillna(X.median()).sum(axis=1).to_numpy()
    aucs = [roc_auc_score(y[test], total[test]) for _, test in OUTER.split(X, y)]
    return {"auc": _summary(aucs), "fold_auc": aucs, "pooled_auc": round(float(roc_auc_score(y, total)), 4)}


def _pick_model(results: dict) -> str:
    """Tek standart hata kuralı: en iyi ortalama AUC'nin 1 SE'si içindeki en basit model."""
    n = OUTER.get_n_splits()
    best = max(results, key=lambda k: np.mean(results[k]["fold_metrics"]["auc"]))
    best_auc = np.asarray(results[best]["fold_metrics"]["auc"])
    floor = best_auc.mean() - best_auc.std(ddof=1) / np.sqrt(n)
    for key in CANDIDATES:  # basitten karmaşığa
        if np.mean(results[key]["fold_metrics"]["auc"]) >= floor:
            return key
    return best


def _operating_threshold(y: np.ndarray, proba: np.ndarray) -> float:
    """Tarama aracı için: duyarlılık >= hedef olan en yüksek eşik."""
    for t in np.round(np.arange(0.95, 0.04, -0.01), 2):
        if _sens_spec(y, proba, t)[0] >= TARGET_SENSITIVITY:
            return float(t)
    return 0.05


def _model_report(key: str, label: str, res: dict, y: np.ndarray, baseline_folds: list[float]) -> dict:
    fm = res["fold_metrics"]
    oof = res["oof_proba"]
    fpr, tpr, _ = roc_curve(y, oof)
    keep = np.unique(np.linspace(0, len(fpr) - 1, min(len(fpr), 60)).astype(int))
    wins = float(np.mean(np.asarray(fm["auc"]) > np.asarray(baseline_folds)))
    return {
        "key": key,
        "label": label,
        "auc": _summary(fm["auc"]),
        "brier": _summary(fm["brier"]),
        "sensitivity_at_0_5": _summary(fm["sensitivity"]),
        "specificity_at_0_5": _summary(fm["specificity"]),
        "pooled_oof_auc": round(float(roc_auc_score(y, oof)), 4),
        "pooled_oof_auc_ci95": _bootstrap_auc_ci(y, oof),
        "folds_beating_baseline": round(wins, 3),
        "roc_curve": {"fpr": fpr[keep].round(4).tolist(), "tpr": tpr[keep].round(4).tolist()},
    }


def main() -> None:
    started = time.time()
    df = pd.read_csv(DATA_PATH)
    X = df[ALL_FEATURES].apply(pd.to_numeric, errors="coerce")
    y = df[TARGET].astype(int).to_numpy()
    print(f"n={len(y)}  (otizm {y.sum()}, kontrol {len(y) - y.sum()})  dış CV: 5x5, iç CV: 5\n")

    baseline = _baseline(X, y)
    print(f"{'Toplam skor (baseline)':42s} AUC {baseline['auc']['mean']:.3f} ± {baseline['auc']['std']:.3f}")

    results, reports = {}, []
    for key, (label, est, grid) in [*CANDIDATES.items(), (REFERENCE[0], REFERENCE[1:])]:
        t0 = time.time()
        results[key] = nested_cv(X, y, est, grid)
        reports.append(_model_report(key, label, results[key], y, baseline["fold_auc"]))
        r = reports[-1]
        print(
            f"{label:42s} AUC {r['auc']['mean']:.3f} ± {r['auc']['std']:.3f}  "
            f"Brier {r['brier']['mean']:.3f}  ({time.time() - t0:.0f} sn)"
        )

    chosen = _pick_model({k: v for k, v in results.items() if k in CANDIDATES})
    label, estimator, grid = CANDIDATES[chosen]
    oof = results[chosen]["oof_proba"]
    threshold = _operating_threshold(y, oof)
    sens, spec = _sens_spec(y, oof, threshold)
    prob_true, prob_pred = calibration_curve(y, oof, n_bins=6, strategy="quantile")

    # Nihai model: aynı prosedür tüm veride. Seçilen 10 madde uygulamada sorulur.
    final_search = GridSearchCV(clone(estimator), grid, cv=INNER, scoring="roc_auc", n_jobs=-1).fit(X, y)
    selected = X.columns[final_search.best_estimator_.named_steps["select"].support_].tolist()
    clf_params = {k.removeprefix("clf__"): v for k, v in final_search.best_params_.items()}
    final_model = _pipeline(clone(estimator.named_steps["clf"]).set_params(**clf_params), select=False)
    final_model.fit(X[selected], y)

    selected_items = [int(c.removeprefix("qchat").removesuffix("recode")) for c in selected]
    stability = results[chosen]["selection_frequency"]

    meta = {
        "model_version": f"toddler-{date.today().isoformat()}",
        "trained_on": date.today().isoformat(),
        "chosen_model": chosen,
        "chosen_model_label": label,
        "selection_rule": "En yüksek ortalama AUC'nin 1 standart hatası içindeki en basit model",
        "hyperparameters": clf_params,
        "features": selected,
        "items": [{"item": i, "question": ITEMS[i][0], "short": SHORT_LABELS[i], "options": ITEMS[i][1]} for i in selected_items],
        "training_medians": {c: float(X[c].median()) for c in selected},
        "threshold": threshold,
        "operating_point": {"threshold": threshold, "sensitivity": round(sens, 4), "specificity": round(spec, 4)},
        "calibration": {"prob_pred": prob_pred.round(4).tolist(), "prob_true": prob_true.round(4).tolist()},
        "baseline_total_score": {k: v for k, v in baseline.items() if k != "fold_auc"},
        "models": reports,
        "item_selection_frequency": [
            {
                "item": int(c.removeprefix("qchat").removesuffix("recode")),
                "short": SHORT_LABELS[int(c.removeprefix("qchat").removesuffix("recode"))],
                "frequency": float(f),
            }
            for c, f in stability.sort_values(ascending=False).items()
        ],
        "dataset": {
            "name": "Q-CHAT, Polonya kohortu (18-24 ay)",
            "n": len(y),
            "n_asd": int(y.sum()),
            "n_control": int(len(y) - y.sum()),
            "source": "https://data.mendeley.com/datasets/tmpkt2mfkg/2",
            "label_source": "ADOS-2 + ADI-R + DSM-5 klinik değerlendirme",
        },
        "evaluation": {
            "outer_cv": "RepeatedStratifiedKFold(5 kat x 5 tekrar)",
            "inner_cv": "StratifiedKFold(5) — hiperparametre araması ve RFE madde seçimi",
            "threshold_note": "Eşik, dış fold tahminleri (OOF) üzerinden duyarlılık >= 0.90 olacak şekilde seçildi.",
        },
        "versions": {"scikit-learn": sklearn.__version__, "xgboost": xgboost.__version__},
    }

    joblib.dump(final_model, MODEL_PATH)
    META_PATH.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\nSeçilen model : {label}  {clf_params}")
    print(f"Sorulacak maddeler: {selected_items}")
    print(f"Eşik {threshold:.2f}  ->  duyarlılık {sens:.3f}, özgüllük {spec:.3f} (OOF)")
    print(f"Kaydedildi: {MODEL_PATH.name}, {META_PATH.name}  ({time.time() - started:.0f} sn)")


if __name__ == "__main__":
    main()
