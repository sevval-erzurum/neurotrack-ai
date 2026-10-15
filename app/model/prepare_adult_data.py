import pandas as pd

df = pd.read_csv("data/adult.csv")

# SADECE numeric kolonları seç (en garanti yöntem)
df = df.select_dtypes(include=['int64', 'float64'])

# target değişkeni string ise düzelt
if "Class/ASD" in df.columns:
    df["Class/ASD"] = df["Class/ASD"].map({"NO": 0, "YES": 1})

# kaydet
df.to_csv("data/adult_clean.csv", index=False)

print("Temiz dataset hazır!")