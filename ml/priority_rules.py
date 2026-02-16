# backend/app/priority_rules.py

def normalize(text: str) -> str:
    return text.lower()


# =========================
# AMMINISTRAZIONE
# =========================
ADMIN_HIGH = [
    "urgente",
    "scadenza",
    "pagamento",
    "ritardo",
    "emissione fattura",
    "fattura errata",
    "sollecito",
    "blocco"
]

ADMIN_LOW = [
    "elenco",
    "storico",
    "archivio",
    "copia",
    "report",
    "lista",
    "riepilogo"
]


def priority_admin(text: str) -> str:
    t = normalize(text)

    if any(k in t for k in ADMIN_HIGH):
        return "high"
    if any(k in t for k in ADMIN_LOW):
        return "low"
    return "medium"


# =========================
# TECNICO
# =========================
TECH_HIGH = [
    "errore",
    "crash",
    "non funziona",
    "bloccante",
    "down",
    "impossibile",
    "sistema fermo"
]

TECH_LOW = [
    "informazione",
    "configurazione",
    "guida",
    "come fare"
]


def priority_tech(text: str) -> str:
    t = normalize(text)

    if any(k in t for k in TECH_HIGH):
        return "high"
    if any(k in t for k in TECH_LOW):
        return "low"
    return "medium"


# =========================
# COMMERCIALE
# =========================
COMM_HIGH = [
    "offerta",
    "preventivo",
    "urgente",
    "cliente importante",
    "scadenza"
]

COMM_LOW = [
    "informazione",
    "brochure",
    "catalogo"
]


def priority_comm(text: str) -> str:
    t = normalize(text)

    if any(k in t for k in COMM_HIGH):
        return "high"
    if any(k in t for k in COMM_LOW):
        return "low"
    return "medium"


# =========================
# DISPATCHER
# =========================
def compute_priority(category: str, text: str) -> str:
    if category == "Amministrazione":
        return priority_admin(text)
    if category == "Tecnico":
        return priority_tech(text)
    if category == "Commerciale":
        return priority_comm(text)

    return "medium"
