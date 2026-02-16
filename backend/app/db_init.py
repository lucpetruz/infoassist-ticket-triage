from werkzeug.security import generate_password_hash
from app.extensions import db
from app.models.user import User


def init_db():
    if User.query.count() == 0:
        users = [
            User(username="admin",
                 password_hash=generate_password_hash("admin123"),
                 role="admin"),
            User(username="commerciale",
                 password_hash=generate_password_hash("comm123"),
                 role="commerciale"),
            User(username="contabile",
                 password_hash=generate_password_hash("cont123"),
                 role="contabile"),
            User(username="assistenza",
                 password_hash=generate_password_hash("assist123"),
                 role="assistenza"),
        ]
        db.session.add_all(users)
        db.session.commit()
