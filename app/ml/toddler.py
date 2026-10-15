"""Q-CHAT tarama modeli: tahmin ve madde bazlı açıklama."""

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

MODEL_DIR = Path(__file__).resolve().parents[1] / "model"
HIGH_RISK_PROBA = 0.75


@dataclass(frozen=True)
class Contribution:
    item: int
    short: str
    answer: int
    log_odds: float


@dataclass(frozen=True)
class Screening:
    probability: float
    risk_level: str  # "low" | "elevated" | "high"
    threshold: float
    contributions: list[Contribution]
    model_version: str


@lru_cache(maxsize=1)
def load() -> tuple[object, dict]:
    model = joblib.load(MODEL_DIR / "toddler_model.pkl")
    meta = json.loads((MODEL_DIR / "toddler_model_meta.json").read_text(encoding="utf-8"))
    return model, meta


def _contributions(model, meta: dict, row: pd.DataFrame) -> np.ndarray:
    """Her maddenin log-odds katkısı, eğitim verisindeki ortalama çocuğa göre.

    Doğrusal modelde bu, özellik bağımsızlığı varsayımıyla tam SHAP değeridir.
    Diğer modeller için maddeyi eğitim medyanına çekip log-odds değişimine bakılır.
    """
    clf = model.named_steps["clf"]
    if hasattr(clf, "coef_"):
        z = model[:-1].transform(row)[0]
        return clf.coef_[0] * z

    def log_odds(frame: pd.DataFrame) -> float:
        p = float(np.clip(model.predict_proba(frame)[0, 1], 1e-6, 1 - 1e-6))
        return np.log(p / (1 - p))

    full = log_odds(row)
    out = []
    for col in meta["features"]:
        occluded = row.copy()
        occluded[col] = meta["training_medians"][col]
        out.append(full - log_odds(occluded))
    return np.asarray(out)


def screen(answers: dict[int, int]) -> Screening:
    model, meta = load()
    items = [entry["item"] for entry in meta["items"]]

    missing = set(items) - set(answers)
    if missing:
        raise ValueError(f"Eksik madde yanıtları: {sorted(missing)}")
    if any(not 0 <= answers[i] <= 4 for i in items):
        raise ValueError("Madde puanları 0-4 aralığında olmalıdır")

    row = pd.DataFrame([[answers[i] for i in items]], columns=meta["features"], dtype=float)
    probability = float(model.predict_proba(row)[0, 1])
    threshold = meta["threshold"]

    if probability >= HIGH_RISK_PROBA:
        level = "high"
    elif probability >= threshold:
        level = "elevated"
    else:
        level = "low"

    contribs = _contributions(model, meta, row)
    contributions = sorted(
        (
            Contribution(item=e["item"], short=e["short"], answer=answers[e["item"]], log_odds=round(float(c), 4))
            for e, c in zip(meta["items"], contribs)
        ),
        key=lambda c: abs(c.log_odds),
        reverse=True,
    )

    return Screening(
        probability=round(probability, 4),
        risk_level=level,
        threshold=threshold,
        contributions=contributions,
        model_version=meta["model_version"],
    )
