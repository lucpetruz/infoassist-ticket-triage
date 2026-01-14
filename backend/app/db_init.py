from .db import engine, SessionLocal
from .models import Base, User
from werkzeug.security import generate_password_hash


def init_db():
    # Crea tutte le tabelle
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()

    # Seed utenti solo se la tabella è vuota
    if session.query(User).count() == 0:
        users = [
            User(username="admin", password_hash=generate_password_hash("admin123"), role="admin"),
            User(username="commerciale", password_hash=generate_password_hash("comm123"), role="commerciale"),
            User(username="contabile", password_hash=generate_password_hash("cont123"), role="contabile"),
            User(username="assistenza", password_hash=generate_password_hash("assist123"), role="assistenza"),
        ]
        session.add_all(users)
        session.commit()

    session.close()


if __name__ == "__main__":
    init_db()
    print("Database inizializzato")
