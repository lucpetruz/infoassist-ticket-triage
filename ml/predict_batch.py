import sys
from pathlib import Path

# rende visibile la root del progetto (infoassist-ticket-triage)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))
import pandas as pd
import re
import joblib


from pathlib import Path

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# PRIORITY RULES (CENTRALIZZATE)
from priority_rules import compute_priority

# =====================
# PATHS (ROBUSTI)
# =====================
BASE_DIR = Path(__file__).resolve().parent      # .../ml
DATA_DIR = BASE_DIR / "data"                    # .../ml/data
MODELS_DIR = BASE_DIR / "models"                # .../ml/models

INPUT_CSV = DATA_DIR / "tickets_new.csv"
OUTPUT_CSV = DATA_DIR / "tickets_predicted.csv"

# =====================
# PREPROCESSING
# =====================
STOPWORDS = set(stopwords.words("italian")) - {"non"}

def preprocess(text: str) -> str:
    if text is None:
        return ""

    if not isinstance(text, str):
        text = str(text)

    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)

    tokens = word_tokenize(text, language="italian")
    tokens = [t for t in tokens if t.isalpha() and t not in STOPWORDS]

    return " ".join(tokens)

# =====================
# INPUT LOADER
# =====================
def load_input_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"File non trovato: {path}")

    df = pd.read_csv(path)

    # accetta sia subject che title
    if "subject" in df.columns and "title" not in df.columns:
        df = df.rename(columns={"subject": "title"})

    required = {"title", "body"}
    if not required.issubset(set(df.columns)):
        raise ValueError(
            f"CSV deve contenere colonne {required}. "
            f"Colonne trovate: {list(df.columns)}"
        )

    return df

# =====================
# MAIN
# =====================
def main():
    # carica dati
    df = load_input_csv(INPUT_CSV)

    # preprocessing testo
    df["text"] = (
        df["title"].fillna("") + " " + df["body"].fillna("")
    ).apply(preprocess)

    # carica modelli ML
    vectorizer = joblib.load(MODELS_DIR / "vectorizer.joblib")
    category_model = joblib.load(MODELS_DIR / "category_model.joblib")

    # trasformazione
    X = vectorizer.transform(df["text"])

    # ===== CATEGORY (ML) =====
    cat_pred = category_model.predict(X)
    cat_proba = category_model.predict_proba(X).max(axis=1)

    # ===== OUTPUT =====
    out = df.copy()
    out["pred_category"] = cat_pred
    out["category_confidence"] = cat_proba.round(3)

    # ===== PRIORITY (RULE-BASED, INTRA-DIPARTIMENTALE) =====
    out["pred_priority"] = out.apply(
        lambda r: compute_priority(
            r["pred_category"],
            f"{r['title']} {r['body']}"
        ),
        axis=1
    )

    # pulizia
    out.drop(columns=["text"], inplace=True)

    # salva output
    out.to_csv(OUTPUT_CSV, index=False)

    print(f"✅ Predizioni salvate in: {OUTPUT_CSV}")
    print("\nDistribuzione categorie predette:")
    print(out["pred_category"].value_counts())

    print("\nDistribuzione priorità predette:")
    print(out["pred_priority"].value_counts())

# =====================
# ENTRYPOINT
# =====================
if __name__ == "__main__":
    main()
