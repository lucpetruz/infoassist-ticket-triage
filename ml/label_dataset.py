import pandas as pd
import re

# =========================
# KEYWORDS (RULE-BASED)
# =========================

CATEGORY_KEYWORDS = {
    "Amministrazione": [
        "fattura", "pagamento", "bonifico", "iva", "scadenza",
        "nota di credito", "credito", "debito", "contabilità"
    ],
    "Tecnico": [
        "errore", "problema", "server", "pc", "computer", "login",
        "crash", "sistema", "rete", "stampante", "software", "hardware"
    ],
    "Commerciale": [
        "offerta", "preventivo", "ordine", "contratto",
        "acquisto", "prezzo", "commerciale", "vendita"
    ]
}

PRIORITY_KEYWORDS = {
    "alta": [
        "urgente", "bloccante", "errore grave", "non funziona",
        "fermo", "down", "impossibile"
    ],
    "media": [
        "problema", "malfunzionamento", "lento", "difficoltà"
    ],
    "bassa": [
        "informazione", "chiarimento", "richiesta", "domanda",
        "copia", "duplicato"
    ]
}

# =========================
# TEXT PREPROCESSING
# =========================

def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    return text

# =========================
# CATEGORY ASSIGNMENT
# =========================

def assign_category(text: str) -> str:
    scores = {cat: 0 for cat in CATEGORY_KEYWORDS}

    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                scores[category] += 1

    # pick category with max score
    best_category = max(scores, key=scores.get)

    # if all scores are zero → noise → default Tecnico
    if scores[best_category] == 0:
        return "Tecnico"

    return best_category

# =========================
# PRIORITY ASSIGNMENT
# =========================

def assign_priority(text: str) -> str:
    for priority, keywords in PRIORITY_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                return priority
    return "media"

# =========================
# MAIN
# =========================

def main():
    df = pd.read_csv("ml/data/tickets.csv")
    print("CSV caricato, numero righe:", len(df))
    # normalizziamo i nomi colonne
    df = df.rename(columns={
        "subject": "title"
    })

    labeled_rows = []

    for idx, row in df.iterrows():
        full_text = f"{row['title']} {row['body']}"
        clean = clean_text(full_text)

        category = assign_category(clean)
        priority = assign_priority(clean)

        labeled_rows.append({
            "id": idx + 1,
            "title": row["title"],
            "body": row["body"],
            "category": category,
            "priority": priority
        })

    labeled_df = pd.DataFrame(labeled_rows)
    print("Scrittura file tickets_labeled.csv in ml/data/")
    labeled_df.to_csv(
        "ml/data/tickets_labeled.csv",
        index=False
    )

    print("Dataset etichettato creato:")
    print(labeled_df["category"].value_counts())
    print(labeled_df["priority"].value_counts())


if __name__ == "__main__":
    main()
