"""Küçük çocuk (18-24 ay) otizm ön tarama modeli — Q-CHAT.

Bu model, projedeki diğer modellerden farklı olarak GERÇEK klinik tanıyı
(ADOS-2/ADI-R/DSM-5) hedefler. adult.csv / child.csv setlerinde hedef, anket
skorunun deterministik türeviydi; orada modelin öğreneceği bir şey yoktu.
Ayrıntı için data/README.md.

Çalıştırma:
    python app/model/train_toddler_model.py
"""

import json
import os

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import RepeatedStratifiedKFold, cross_val_predict, cross_val_score
from sklearn.pipeline import Pipeline

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_PATH = os.path.join(BASE_DIR, "data", "qchat_toddler_poland.csv")
MODEL_DIR = os.path.join(BASE_DIR, "app", "model")
MODEL_PATH = os.path.join(MODEL_DIR, "toddler_model.pkl")
META_PATH = os.path.join(MODEL_DIR, "toddler_model_meta.json")

TARGET = "asd"

# Uygulamada 10 soru soruluyor. RFE ile seçilen bu 10 madde, 25 maddenin
# performansını pratik olarak koruyor (AUC 0.942 vs 0.947).
SELECTED_ITEMS = [1, 2, 3, 4, 5, 6, 9, 15, 19, 25]
FEATURES = [f"qchat{i}recode" for i in SELECTED_ITEMS]

# Q-CHAT madde başlıkları (Allison ve ark.; Polonya çalışması Tablo 2).
ITEM_LABELS = {
    1: "Adıyla seslenildiğinde bakma",
    2: "Göz teması",
    3: "Nesneleri sıraya dizme",
    4: "Çocuğun konuşmasının anlaşılırlığı",
    5: "İstediğini işaret etme",
    6: "İlgisini paylaşmak için işaret etme",
    9: "-mış gibi oyun",
    15: "Üzgün birini teselli etme",
    19: "Jest kullanımı",
    25: "Amaçsızca boşluğa bakma",
}

RANDOM_STATE = 42


def build_model() -> Pipeline:
    return Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            (
                "classifier",
                RandomForestClassifier(
                    n_estimators=400,
                    min_samples_leaf=2,
                    class_weight="balanced",
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )


def evaluate(X: pd.DataFrame, y: pd.Series) -> dict:
    """Tekrarlı çapraz doğrulama. Tek bir train/test bölmesi n=252'de çok gürültülü."""
    cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=4, random_state=RANDOM_STATE)

    auc = cross_val_score(build_model(), X, y, cv=cv, scoring="roc_auc")
    acc = cross_val_score(build_model(), X, y, cv=cv, scoring="accuracy")
    sens = cross_val_score(build_model(), X, y, cv=cv, scoring="recall")

    # Özgüllük = negatif sınıfın duyarlılığı
    proba = cross_val_predict(build_model(), X, y, cv=5, method="predict_proba")[:, 1]
    pred = (proba >= 0.5).astype(int)
    spec = ((pred == 0) & (y == 0)).sum() / max((y == 0).sum(), 1)

    # Karşılaştırma: klasik toplam-skor eşiği ne yapıyor?
    total = X.sum(axis=1)
    baseline_auc = roc_auc_score(y, total)

    return {
        "auc_mean": round(float(auc.mean()), 4),
        "auc_std": round(float(auc.std()), 4),
        "accuracy_mean": round(float(acc.mean()), 4),
        "sensitivity_mean": round(float(sens.mean()), 4),
        "specificity": round(float(spec), 4),
        "baseline_total_score_auc": round(float(baseline_auc), 4),
    }


def main() -> None:
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(
            f"Veri seti bulunamadı: {DATA_PATH}\nKaynak: https://data.mendeley.com/datasets/tmpkt2mfkg/2"
        )

    df = pd.read_csv(DATA_PATH)

    missing = [c for c in FEATURES + [TARGET] if c not in df.columns]
    if missing:
        raise ValueError(f"Veri setinde beklenen kolonlar yok: {missing}")

    X = df[FEATURES].apply(pd.to_numeric, errors="coerce")
    y = df[TARGET].astype(int)

    metrics = evaluate(X, y)

    print("Küçük çocuk (Q-CHAT) modeli — çapraz doğrulama sonuçları")
    print(f"  n = {len(df)}  (otizm {int(y.sum())}, kontrol {int((1 - y).sum())})")
    print(f"  AUC          : {metrics['auc_mean']:.3f} ± {metrics['auc_std']:.3f}")
    print(f"  Doğruluk     : {metrics['accuracy_mean']:.3f}")
    print(f"  Duyarlılık   : {metrics['sensitivity_mean']:.3f}")
    print(f"  Özgüllük     : {metrics['specificity']:.3f}")
    print(f"  Karşılaştırma: toplam skor eşiği AUC {metrics['baseline_total_score_auc']:.3f}")

    # Nihai model tüm veriyle eğitilir; yukarıdaki metrikler CV'den gelir.
    model = build_model().fit(X, y)

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    meta = {
        "features": FEATURES,
        "item_labels": {str(k): v for k, v in ITEM_LABELS.items()},
        "item_scale": "0-4 (yüksek = atipik davranış)",
        "target": "asd (1 = otizm, 0 = kontrol)",
        "age_range_months": [18, 24],
        "n_samples": int(len(df)),
        "metrics_cv": metrics,
        "data_source": "https://data.mendeley.com/datasets/tmpkt2mfkg/2",
        "label_source": "ADOS-2 + ADI-R + DSM-5 klinik değerlendirme",
    }

    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"\nModel kaydedildi : {MODEL_PATH}")
    print(f"Meta kaydedildi  : {META_PATH}")


if __name__ == "__main__":
    main()
