import pandas as pd
import re
import nltk
import joblib
import matplotlib.pyplot as plt

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

STOPWORDS = set(stopwords.words("italian"))

def preprocess(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    tokens = word_tokenize(text, language="italian")
    tokens = [t for t in tokens if t.isalpha() and t not in STOPWORDS]
    return " ".join(tokens)

df = pd.read_csv("ml/data/tickets.csv")
df["text"] = (df["subject"] + " " + df["body"]).apply(preprocess)

vectorizer = joblib.load("ml/models/vectorizer.joblib")
cat_model = joblib.load("ml/models/category_model.joblib")
prio_model = joblib.load("ml/models/priority_model.joblib")

# CATEGORY
Xtr, Xte, ytr, yte = train_test_split(
    df["text"], df["category"],
    test_size=0.2, random_state=42, stratify=df["category"]
)
Xte_vec = vectorizer.transform(Xte)
y_pred = cat_model.predict(Xte_vec)

cm = confusion_matrix(yte, y_pred, labels=cat_model.classes_)
disp = ConfusionMatrixDisplay(cm, display_labels=cat_model.classes_)
disp.plot(cmap="Blues")
plt.title("Confusion Matrix - Category")
plt.show()

# PRIORITY
Xtrp, Xtep, ytrp, ytep = train_test_split(
    df["text"], df["priority"],
    test_size=0.2, random_state=42, stratify=df["priority"]
)
Xtep_vec = vectorizer.transform(Xtep)
yp_pred = prio_model.predict(Xtep_vec)

cm_p = confusion_matrix(ytep, yp_pred, labels=prio_model.classes_)
disp_p = ConfusionMatrixDisplay(cm_p, display_labels=prio_model.classes_)
disp_p.plot(cmap="Greens")
plt.title("Confusion Matrix - Priority")
plt.show()
