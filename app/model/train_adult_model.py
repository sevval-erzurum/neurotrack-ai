import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

# Orijinal yetişkin dataseti
df = pd.read_csv("data/adult.csv")

# Sadece kullanacağımız kolonlar
feature_columns = [
    "A1_Score",
    "A2_Score",
    "A3_Score",
    "A4_Score",
    "A5_Score",
    "A6_Score",
    "A7_Score",
    "A8_Score",
    "A9_Score",
    "A10_Score",
    "age"
]

target_column = "Class/ASD"

# Gerekli kolonları seç
df = df[feature_columns + [target_column]].copy()

# Hedef değişkeni sayıya çevir
df[target_column] = df[target_column].map({"NO": 0, "YES": 1})

# Tüm feature'ları sayıya çevir
for col in feature_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Eksik satırları sil
df = df.dropna()

# X ve y
X = df[feature_columns]
y = df[target_column]

# Eğitim / test bölme
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Model
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# Kaydet
joblib.dump(model, "app/model/adult_model.pkl")

print("Adult model oluşturuldu!")
print("X shape:", X.shape)
print("y unique:", y.unique())