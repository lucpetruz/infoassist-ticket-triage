import joblib
import numpy as np
import pandas as pd

# =====================
# LOAD MODELS
# =====================
vectorizer = joblib.load("ml/models/vectorizer.joblib")
cat_model = joblib.load("ml/models/category_model.joblib")
prio_model = joblib.load("ml/models/priority_model.joblib")

feature_names = np.array(vectorizer.get_feature_names_out())

def top_features_per_class(model, feature_names, top_n=5):
    results = {}
    for idx, class_label in enumerate(model.classes_):
        coefs = model.coef_[idx]
        top_positive = np.argsort(coefs)[-top_n:][::-1]
        results[class_label] = feature_names[top_positive]
    return results

# =====================
# CATEGORY FEATURES
# =====================
cat_features = top_features_per_class(cat_model, feature_names)

print("\nTOP 5 parole più influenti per CATEGORIA:\n")
for cls, words in cat_features.items():
    print(f"{cls}: {', '.join(words)}")

# =====================
# PRIORITY FEATURES
# =====================
prio_features = top_features_per_class(prio_model, feature_names)

print("\nTOP 5 parole più influenti per PRIORITÀ:\n")
for cls, words in prio_features.items():
    print(f"{cls}: {', '.join(words)}")
