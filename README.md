# InfoAssist Ticket Triage
Applicazione per la classificazione automatica dei ticket di assistenza aziendale, 
basato su tecniche di Machine Learning, integrato con front-end web.
L'obiettivo è di automatizzare lo smistamento di ticket, che giungono in un'azienda che si occupa di IT, 
verso il dipartimento corretto, assegnando anche una priorità operativa.
URL ESTERNO PER RAGGIUNGERE IL FRONT END: https://infoassi-tk-tri.datalabcentre.com/
**Obiettivo del progetto**
L’obiettivo che si propone l'elaborato è realizzare un prototipo(essenziale, riproducibile e comprensibile) che:

- riceva ticket testuali (titolo + descrizione)

- classifichi automaticamente:
                              - Categoria: Amministrazione / Commerciale / Tecnico

                              - Priorità: bassa / media / alta


- permetta di:
               - addestrare e valutare il modello ML

               - applicare il modello a nuovi ticket  

visualizzare e scaricare i risultati tramite interfaccia web.

**Architettura generale**
Il progetto è strutturato con separazione tra le componenti:
Frontend (HTML + Bootstrap)
        ↓
Backend (Flask – API & UI)
        ↓
Machine Learning (scikit-learn)

**Considerazioni:**
Il Machine Learning è indipendente dall’interfaccia web
Il Backend Flask funge da collettore tra le parti
Il Frontend gestisce solo la presentazione

Questa struttura rende il progetto molto simile ad un caso reale,
avendo le caratteristiche ottimali di gestione e replicabilità.

**Alberatura strutturale del progetto **

infoassist-ticket-triage/
│
├── .venv/                       # Virtual environment Python
│
├── backend/                     # Backend Flask
│   │
│   ├── run.py                   # Entry point dell'app Flask
│   │
│   ├── app/
│   │   ├── __init__.py          # App factory Flask
│   │   │
│   │   ├── routes_ui.py         # Route frontend (upload, dashboard, form)
│   │   ├── routes_predict.py    # API di predizione (ticket singolo / batch)
│   │   │
│   │   ├── ml_service.py        # Servizio ML + priority rule-based
│   │   │
│   │   ├── services/
│   │   │   ├── ticket_service.py  # Logica di persistenza DB ticket
│   │   │   └── __init__.py
│   │   │
│   │   ├── models/              # Modelli ORM / DB (se presenti)
│   │   │
│   │   ├── templates/           # Template HTML (Bootstrap)
│   │   │   ├── base.html
│   │   │   ├── upload.html
│   │   │   ├── dashboard.html
│   │   │   └── ...
│   │   │
│   │   ├── static/              # Asset statici
│   │   │   ├── css/
│   │   │   ├── js/
│   │   │   └── images/
│   │   │
│   │   └── extensions.py        # DB, migrate, ecc.
│   │
│   └── migrations/              # Migrazioni database (se usate)
│
├── ml/                          # Modulo Machine Learning
│   │
│   ├── data/                    # Dataset
│   │   ├── tickets_labeled.csv
│   │   ├── tickets_retrained.csv
│   │   ├── tickets_new.csv
│   │   └── tickets_predicted.csv
│   │
│   ├── models/                  # Artefatti ML
│   │   ├── vectorizer.joblib
│   │   └── category_model.joblib
│   │
│   ├── train.py                 # Training modello categoria
│   ├── merge_retraining.py      # Merge dati + retraining
│   ├── predict_batch.py         # Predizione batch standalone
│   │
│   └── priority_rules.py        # Regole di priorità intra-dipartimentali
│
├── docker/                      # File docker (non usati in runtime attuale)
│
├── docker-compose.yml           # Orchestrazione (opzionale)
│
├── data/                        # Output o export (separato da ml/data)
│
├── .env                         # Variabili ambiente
├── .gitignore
├── README.md
└── result.csv                   # Output di test / sperimentazioni


**Installazione e avvio**
Creare e attivare l’ambiente virtuale
python -m venv .venv
.\.venv\Scripts\Activate.ps1

**Installare le dipendenze**
pip install -r backend/requirements.txt

**Avviare l’applicazione web**
python -m backend.app.main

L’app sarà disponibile, in locale, all'indirizzo:
http://127.0.0.1:5000

**Pipeline Machine Learning**
Creazione dataset supervisionato
python ml/label_dataset.py
( Viene generato un dataset etichettato (tickets_labeled.csv) basato su keyword).

**Addestramento dei modelli**
python ml/train.py

**TF-IDF + Logistic Regression**
Modelli separati per categoria e priorità
Salvataggio dei modelli in ml/models/

**Valutazione**
python ml/evaluate.py
python ml/confusion_matrix.py

**Metriche utilizzate:**
Accuracy
F1 macro
Confusion Matrix

**Interpretabilità**
python ml/feature_importance.py

**Estrazione delle parole più influenti per Categoria e Priorità.**
Predizione su nuovi ticket
python ml/predict_batch.py

Input: CSV non etichettato
Output: CSV con categoria e priorità previste

**Interfaccia Web**
L’interfaccia web consente di:
- effettuare login simulato per ruolo (Admin, Tecnico, Commerciale, Contabile)
- caricare un file CSV di ticket
- inserire un singolo ticket
- ottenere automaticamente:
                          - categoria
                          - priorità
- scaricare il file CSV risultante
- visualizzazione dei ticket a 7/30/90 giorni con metriche e classificazione visibile su pagine web
- visualizzazione dei ticket in base al dipartimento di appartenenza

Il layout utilizza Bootstrap, con branding aziendale e logo integrato come sfondo.

**Tecnologie utilizzate**
Python 3.12
Flask
scikit-learn
NLTK
pandas / numpy
matplotlib
Bootstrap 5
PostgreSQL  

**Stato del progetto**
 - Pipeline ML completa
 - Modelli addestrati e salvati
 - Valutazione e interpretabilità
 -  Web app funzionante
 -  Architettura modulare

