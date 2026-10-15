import os
import re
import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_PATH = os.path.join(BASE_DIR, "data", "child.csv")
MODEL_DIR = os.path.join(BASE_DIR, "app", "model")
MODEL_PATH = os.path.join(MODEL_DIR, "child_model.pkl")


def normalize_column_name(name):
    return re.sub(r"[^a-zA-Z0-9]", "", str(name)).lower()


def find_column(df, candidates):
    normalized_map = {
        normalize_column_name(column): column
        for column in df.columns
    }

    for candidate in candidates:
        key = normalize_column_name(candidate)
        if key in normalized_map:
            return normalized_map[key]

    return None


def convert_target(value):
    value = str(value).strip().lower()

    positive_values = ["yes", "y", "1", "true", "asd", "autism", "evet"]
    negative_values = ["no", "n", "0", "false", "not asd", "hayır", "hayir"]

    if value in positive_values:
        return 1

    if value in negative_values:
        return 0

    if "yes" in value:
        return 1

    if "no" in value:
        return 0

    raise ValueError(f"Hedef değer dönüştürülemedi: {value}")


def main():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Veri seti bulunamadı: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)
    df.columns = [str(column).strip() for column in df.columns]

    feature_candidates = {
        "A1_Score": ["A1_Score", "A1", "A1 score"],
        "A2_Score": ["A2_Score", "A2", "A2 score"],
        "A3_Score": ["A3_Score", "A3", "A3 score"],
        "A4_Score": ["A4_Score", "A4", "A4 score"],
        "A5_Score": ["A5_Score", "A5", "A5 score"],
        "A6_Score": ["A6_Score", "A6", "A6 score"],
        "A7_Score": ["A7_Score", "A7", "A7 score"],
        "A8_Score": ["A8_Score", "A8", "A8 score"],
        "A9_Score": ["A9_Score", "A9", "A9 score"],
        "A10_Score": ["A10_Score", "A10", "A10 score"],
        "age": ["age", "Age"],
    }

    selected_columns = {}

    for standard_name, candidates in feature_candidates.items():
        found_column = find_column(df, candidates)

        if found_column is None:
            raise ValueError(f"Gerekli sütun bulunamadı: {standard_name}")

        selected_columns[standard_name] = found_column

    target_column = find_column(
        df,
        [
            "Class/ASD",
            "Class/ASD Traits",
            "Class_ASD",
            "class",
            "Class",
            "ASD",
            "ASD_traits",
            "target",
            "Target",
        ],
    )

    if target_column is None:
        raise ValueError("Hedef sütun bulunamadı. Örn: Class/ASD")

    X = pd.DataFrame()

    for standard_name, original_column in selected_columns.items():
        X[standard_name] = pd.to_numeric(df[original_column], errors="coerce")

    y = df[target_column].apply(convert_target)

    valid_rows = X.notna().all(axis=1)
    X = X[valid_rows]
    y = y[valid_rows]

    if len(X) == 0:
        raise ValueError("Eğitim için geçerli veri kalmadı.")

    stratify_value = y if y.value_counts().min() >= 2 else None

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=stratify_value,
    )

    model = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            (
                "classifier",
                RandomForestClassifier(
                    n_estimators=200,
                    max_depth=8,
                    min_samples_leaf=2,
                    random_state=42,
                    class_weight="balanced",
                ),
            ),
        ]
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)

    print("Çocuk modeli eğitildi.")
    print(f"Accuracy: {accuracy:.4f}")
    print(classification_report(y_test, predictions))

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    print(f"Model kaydedildi: {MODEL_PATH}")


if __name__ == "__main__":
    main()