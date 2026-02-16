# backend/app/ml_service.py

import sys
from pathlib import Path

# =========================
# PYTHONPATH (ROOT PROGETTO)
# =========================
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

import os
import re
import pandas as pd
import joblib

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Regole di PRIORITY (file: ml/priority_rules.py)
from ml.priority_rules import compute_priority

# =========================
# PATH MODELLI
# =========================
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ML_MODELS_DIR = os.path.join(BASE_DIR, "ml", "models")

VECTORIZER_PATH = os.path.join(ML_MODELS_DIR, "vectorizer.joblib")
CATEGORY_MODEL_PATH = os.path.join(ML_MODELS_DIR, "category_model.joblib")

# =========================
# LOAD MODELLI
# =========================
vectorizer = joblib.load(VECTORIZER_PATH)
category_model = joblib.load(CATEGORY_MODEL_PATH)

# =========================
# NLP
# =========================
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

# =========================
# CSV PREDICTION (UPLOAD)
# =========================
def predict_from_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    # accetta subject al posto di title
    if "subject" in df.columns and "title" not in df.columns:
        df = df.rename(columns={"subject": "title"})

    required = {"title", "body"}
    if not required.issubset(df.columns):
        raise ValueError("Il CSV deve contenere le colonne: title, body")

    # preprocess testo
    df["text"] = (
        df["title"].fillna("") + " " + df["body"].fillna("")
    ).apply(preprocess)

    # vettorizzazione
    X = vectorizer.transform(df["text"])

    # ===== CATEGORY (ML) =====
    df["category"] = category_model.predict(X)
    df["category_confidence"] = (
        category_model.predict_proba(X).max(axis=1).round(3)
    )

    # ===== PRIORITY (RULE-BASED) =====
    df["priority"] = df.apply(
        lambda r: compute_priority(
            r["category"],
            f"{r['title']} {r['body']}"
        ),
        axis=1
    )

    # confidence deterministica
    df["priority_confidence"] = 1.0

    return df.drop(columns=["text"])

# =========================
# SINGLE TICKET
# =========================
def predict_single_ticket(title: str, body: str):
    raw_text = f"{title} {body}"
    text = preprocess(raw_text)

    X = vectorizer.transform([text])

    category = category_model.predict(X)[0]
    category_conf = round(
        category_model.predict_proba(X).max(), 3
    )

    priority = compute_priority(category, raw_text)

    return {
        "title": title,
        "body": body,
        "category": category,
        "category_confidence": category_conf,
        "priority": priority,
        "priority_confidence": 1.0
    }
