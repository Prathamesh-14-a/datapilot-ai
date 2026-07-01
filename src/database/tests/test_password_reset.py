import importlib


def test_password_reset_token_can_be_created_and_verified(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")

    import src.database.db_connection as db_connection
    import src.database.models as models
    import src.services.passwd_reset as passwd_reset

    db_connection = importlib.reload(db_connection)
    models = importlib.reload(models)
    passwd_reset = importlib.reload(passwd_reset)

    db = db_connection.SessionLocal()
    try:
        user = models.User(username="reset", email="reset@example.com", password_hash="hash")
        db.add(user)
        db.commit()
        db.refresh(user)

        raw_token = passwd_reset.create_reset_token(db, user)
        record = passwd_reset.verify_reset_token(db, raw_token)

        assert record is not None
        assert record.user_id == user.id
    finally:
        db.close()
