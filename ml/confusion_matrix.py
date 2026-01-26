import pandas as pd
import re
import joblib
import matplotlib.pyplot as plt

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

STOPWORDS = set(stopwords.words("italian")) - {"non", "senza"}

def preprocess(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    tokens = word_tokenize(text, language="italian")
    tokens = [t for t in tokens if t.isalpha() and t not in STOPWORDS]
    return " ".join(tokens)

# =====================
# LOAD DATA
# =====================
df = pd.read_csv("ml/data/tickets_labeled.csv")
df["text"] = (df["title"] + " " + df["body"]).apply(preprocess)

vectorizer = joblib.load("ml/models/vectorizer.joblib")
cat_model = joblib.load("ml/models/category_model.joblib")
prio_model = joblib.load("ml/models/priority_model.joblib")

# =====================
# CONFUSION MATRIX - CATEGORY
# =====================
Xtr, Xte, ytr, yte = train_test_split(
    df["text"], df["category"],
    test_size=0.2, random_state=42, stratify=df["category"]
)

Xte_vec = vectorizer.transform(Xte)
y_pred = cat_model.predict(Xte_vec)

cm_cat = confusion_matrix(yte, y_pred, labels=cat_model.classes_)
disp_cat = ConfusionMatrixDisplay(
    confusion_matrix=cm_cat,
    display_labels=cat_model.classes_
)

disp_cat.plot(cmap="Blues")
plt.title("Confusion Matrix - Categoria")
plt.tight_layout()
plt.show()

# =====================
# CONFUSION MATRIX - PRIORITY
# =====================
Xtr_p, Xte_p, ytr_p, yte_p = train_test_split(
    df["text"], df["priority"],
    test_size=0.2, random_state=42, stratify=df["priority"]
)

Xte_p_vec = vectorizer.transform(Xte_p)
y_pred_p = prio_model.predict(Xte_p_vec)

cm_prio = confusion_matrix(yte_p, y_pred_p, labels=prio_model.classes_)
disp_prio = ConfusionMatrixDisplay(
    confusion_matrix=cm_prio,
    display_labels=prio_model.classes_
)

disp_prio.plot(cmap="Greens")
plt.title("Confusion Matrix - Priorità")
plt.tight_layout()
plt.show()
