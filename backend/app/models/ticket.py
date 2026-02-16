from app.extensions import db
from datetime import datetime

class Ticket(db.Model):
    __tablename__ = "tickets"
    __table_args__ = {"schema": "hp"}  

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.Text, nullable=False)
    body = db.Column(db.Text, nullable=False)

    category = db.Column(db.String(50), nullable=False)
    priority = db.Column(db.String(20), nullable=True)

    category_confidence = db.Column(db.Float, nullable=True)
    priority_confidence = db.Column(db.Float, nullable=True)

    source = db.Column(db.String(20), nullable=False)  # csv / manual
    created_by = db.Column(db.String(50), nullable=True)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    def __repr__(self):
        return f"<Ticket {self.id} {self.category} {self.priority}>"

