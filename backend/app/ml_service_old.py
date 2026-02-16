import pandas as pd
import re
import joblib

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

STOPWORDS = set(stopwords.words("italian")) - {"non"}

def preprocess(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    tokens = word_tokenize(text, language="italian")
    tokens = [t for t in tokens if t.isalpha() and t not in STOPWORDS]
    return " ".join(tokens)

def predict_from_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    # accetta subject o title
    if "subject" in df.columns and "title" not in df.columns:
        df = df.rename(columns={"subject": "title"})

    required = {"title", "body"}
    if not required.issubset(df.columns):
        raise ValueError("Il CSV deve contenere le colonne: title, body")

    df["text"] = (df["title"].fillna("") + " " + df["body"].fillna("")).apply(preprocess)

    vectorizer = joblib.load("ml/models/vectorizer.joblib")
    cat_model = joblib.load("ml/models/category_model.joblib")
    prio_model = joblib.load("ml/models/priority_model.joblib")

    X = vectorizer.transform(df["text"])

    df["pred_category"] = cat_model.predict(X)
    df["pred_priority"] = prio_model.predict(X)
    df["category_confidence"] = cat_model.predict_proba(X).max(axis=1).round(3)
    df["priority_confidence"] = prio_model.predict_proba(X).max(axis=1).round(3)

    return df.drop(columns=["text"])
