import pandas as pd
import re
import joblib

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

STOPWORDS = set(stopwords.words("italian")) - {"non"}  # manteniamo "non"

def preprocess(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    tokens = word_tokenize(text, language="italian")
    tokens = [t for t in tokens if t.isalpha() and t not in STOPWORDS]
    return " ".join(tokens)

def load_input_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    # accetta sia subject che title
    if "subject" in df.columns and "title" not in df.columns:
        df = df.rename(columns={"subject": "title"})

    required = {"title", "body"}
    if not required.issubset(set(df.columns)):
        raise ValueError(f"CSV deve contenere colonne {required}. Colonne trovate: {list(df.columns)}")

    return df

def main():
    input_path = "ml/data/tickets_new.csv"
    output_path = "ml/data/tickets_predicted.csv"

    df = load_input_csv(input_path)
    df["text"] = (df["title"].fillna("") + " " + df["body"].fillna("")).apply(preprocess)

    vectorizer = joblib.load("ml/models/vectorizer.joblib")
    cat_model = joblib.load("ml/models/category_model.joblib")
    prio_model = joblib.load("ml/models/priority_model.joblib")

    X = vectorizer.transform(df["text"])

    # ===== CATEGORY =====
    cat_pred = cat_model.predict(X)
    cat_proba = cat_model.predict_proba(X).max(axis=1)

    # ===== PRIORITY =====
    prio_pred = prio_model.predict(X)
    prio_proba = prio_model.predict_proba(X).max(axis=1)

    out = df.copy()
    out["pred_category"] = cat_pred
    out["pred_priority"] = prio_pred
    out["category_confidence"] = cat_proba.round(3)
    out["priority_confidence"] = prio_proba.round(3)

    # teniamo anche il testo originale, ma possiamo rimuovere "text" se non serve
    out.drop(columns=["text"], inplace=True)

    out.to_csv(output_path, index=False)
    print(f"✅ Predizioni salvate in: {output_path}")
    print("Distribuzione categorie predette:\n", out["pred_category"].value_counts())
    print("Distribuzione priorità predette:\n", out["pred_priority"].value_counts())

if __name__ == "__main__":
    main()
