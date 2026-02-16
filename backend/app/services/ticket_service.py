from app.extensions import db
from app.models.ticket import Ticket

def save_ticket(prediction: dict, source: str, username: str):
    ticket = Ticket(
        title=prediction["title"],
        body=prediction["body"],
        category=prediction["category"],
        priority=prediction["priority"],
        category_confidence=float(prediction["category_confidence"]),
        priority_confidence=float(prediction["priority_confidence"]),
        source=source,
        created_by=username
    )

    db.session.add(ticket)
    db.session.commit()

    return ticket
