import pandas as pd
from pathlib import Path

DATA = Path("ml/data")

# dataset storico
base = pd.read_csv(DATA / "tickets_labeled.csv", encoding="utf-8")

# retraining finale (contabile + commerciale)
retrain = pd.read_csv(DATA / "retrain_final.csv", encoding="utf-8")

print("Base:", base.shape)
print("Retrain:", retrain.shape)

# normalizza nomi colonne
base = base.rename(columns={
    "category": "correct_category"
})

# tieni solo le colonne utili
base = base[["title", "body", "correct_category"]]
retrain = retrain[["title", "body", "correct_category"]]

# concat
df = pd.concat([base, retrain], ignore_index=True)

# pulizia finale
df = df.dropna()
df["correct_category"] = df["correct_category"].str.strip()
out = DATA / "tickets_retrained.csv"
df = df.rename(columns={"correct_category": "category"})
df.to_csv(out, index=False, encoding="utf-8")

print("✔ Dataset finale creato")
print(df["correct_category"].value_counts())
print("Totale righe:", len(df))

