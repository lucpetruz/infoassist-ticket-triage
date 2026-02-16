import pandas as pd
import re
import joblib
import nltk

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score

STOPWORDS = set(stopwords.words("italian")) - {"non", "senza"}
def preprocess(text):
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
# LOAD DATA
# =====================
#df = pd.read_csv("ml/data/tickets_labeled.csv")
df = pd.read_csv("ml/data/tickets_retrained.csv")

# normalizza label colonna categoria
if "category" not in df.columns and "correct_category" in df.columns:
    df = df.rename(columns={"correct_category": "category"})
print(df.columns)
df["title"] = df["title"].fillna("")
df["body"] = df["body"].fillna("")
df["text"] = (df["title"] + " " + df["body"]).apply(preprocess)

print("NaN in text:", df["text"].isna().sum())
print("Text vuoti:", (df["text"].str.strip() == "").sum())

# rimuove righe senza categoria valida
df = df.dropna(subset=["category"])

# elimina stringhe vuote o spazi
df = df[df["category"].str.strip() != ""]
print(df["category"].isna().sum())
print(df["category"].value_counts())

# =====================
# CATEGORY MODEL
# =====================
X_train, X_test, y_train, y_test = train_test_split(
    df["text"], df["category"],
    test_size=0.2, random_state=42, stratify=df["category"]
)

#vectorizer = TfidfVectorizer(max_features=3000, ngram_range=(1,2))
vectorizer = TfidfVectorizer(
    max_features=5000,
    ngram_range=(1, 2),
    min_df=2,
    max_df=0.9
)
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

#cat_model = LogisticRegression(max_iter=1000)
cat_model = LogisticRegression(
    max_iter=1000,
    class_weight="balanced",
     n_jobs=-1
)

cat_model.fit(X_train_vec, y_train)
cat_pred = cat_model.predict(X_test_vec)
from sklearn.metrics import classification_report, confusion_matrix
cat_acc = accuracy_score(y_test, cat_pred)
cat_f1 = f1_score(y_test, cat_pred, average="macro")

print("\n=== VALUTAZIONE MODELLO CATEGORIA ===")
print("Accuracy:", round(cat_acc, 3))
print("F1 macro:", round(cat_f1, 3))

print("\nClassification report:")
print(classification_report(y_test, cat_pred))

print("\nConfusion matrix:")
print(confusion_matrix(y_test, cat_pred))


# =====================
# PRIORITY MODEL
# =====================
#Xp_train, Xp_test, yp_train, yp_test = train_test_split(
 #   df["text"], df["priority"],
  #  test_size=0.2, random_state=42, stratify=df["priority"]
#)

#Xp_train_vec = vectorizer.fit_transform(Xp_train)
#Xp_test_vec = vectorizer.transform(Xp_test)

#prio_model = LogisticRegression(max_iter=1000)
#prio_model.fit(Xp_train_vec, yp_train)
#prio_pred = prio_model.predict(Xp_test_vec)

#prio_acc = accuracy_score(yp_test, prio_pred)
#prio_f1 = f1_score(yp_test, prio_pred, average="macro")

#print("PRIORITY Accuracy:", round(prio_acc, 3))
#print("PRIORITY F1 macro:", round(prio_f1, 3))

# =====================
# SAVE ARTEFACTS
# =====================
joblib.dump(vectorizer, "ml/models/vectorizer.joblib")
joblib.dump(cat_model, "ml/models/category_model.joblib")
#joblib.dump(prio_model, "ml/models/priority_model.joblib")

print("Modelli salvati in ml/models/")
