from datetime import date, timedelta

from jose import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.base import Base
from models.role import Role, RoleName
from models.user import User
from services.auth_service import (
    SECRET_KEY,
    ALGORITHM,
    authenticate_user,
    create_access_token,
    get_password_hash,
    get_user,
    verify_password,
)


import pytest


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    yield db
    db.close()


def test_password_hash_and_verify():
    password = "super-secret"
    hashed = get_password_hash(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong-password", hashed) is False


def test_get_user_returns_user(session):
    role = Role(role_name=RoleName.ADMIN, permissions=[], users=[])
    session.add(role)
    session.commit()
    user = User(
        username="alice",
        password_ash=get_password_hash("secret"),
        is_active=True,
        updated_at=date.today(),
        created_at=date.today(),
        role=role,
        role_id=role.id,
        stock_movements=[],
    )
    session.add(user)
    session.commit()

    found = get_user(session, "alice")
    assert found is not None
    assert found.username == "alice"


def test_get_user_returns_none_if_missing(session):
    assert get_user(session, "unknown") is None


def test_authenticate_user_success(session):
    role = Role(role_name=RoleName.ADMIN, permissions=[], users=[])
    session.add(role)
    session.commit()
    user = User(
        username="bob",
        password_ash=get_password_hash("password123"),
        is_active=True,
        updated_at=date.today(),
        created_at=date.today(),
        role=role,
        role_id=role.id,
        stock_movements=[],
    )
    session.add(user)
    session.commit()

    authenticated = authenticate_user(session, "bob", "password123")
    assert authenticated is not None
    assert authenticated.username == "bob"


def test_authenticate_user_rejects_bad_password(session):
    role = Role(role_name=RoleName.ADMIN, permissions=[], users=[])
    session.add(role)
    session.commit()
    user = User(
        username="charlie",
        password_ash=get_password_hash("password123"),
        is_active=True,
        updated_at=date.today(),
        created_at=date.today(),
        role=role,
        role_id=role.id,
        stock_movements=[],
    )
    session.add(user)
    session.commit()

    assert authenticate_user(session, "charlie", "bad") is None


def test_authenticate_user_rejects_missing_user(session):
    assert authenticate_user(session, "missing", "whatever") is None


def test_create_access_token_contains_subject_and_expiration():
    token = create_access_token({"sub": "alice"}, expires_delta=timedelta(minutes=5))
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    assert payload["sub"] == "alice"
    assert payload["exp"] > 0
