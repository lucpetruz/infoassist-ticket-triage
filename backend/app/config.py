class Config:
    SECRET_KEY = "dev-secret-key"

    SQLALCHEMY_DATABASE_URI = (
        "postgresql://ticket_user:Suuom2fh!@localhost:5432/ticket_triage"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
