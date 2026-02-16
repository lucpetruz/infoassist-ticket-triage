import sys
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")

sys.path.insert(0, BACKEND_DIR)
from app import create_app
from app.models.ticket import Ticket
from app.extensions import db
from app.ml_service import predict_single_ticket

app = create_app()

with app.app_context():
    tickets = Ticket.query.all()
    print(f"Ticket trovati: {len(tickets)}")

    updated = 0

    for t in tickets:
        pred = predict_single_ticket(t.title, t.body)

        if t.category != pred["category"]:
            t.category = pred["category"]
            t.category_confidence = pred["category_confidence"]
            updated += 1

    db.session.commit()
    print(f"Ticket riclassificati: {updated}")
