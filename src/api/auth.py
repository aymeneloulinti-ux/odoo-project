from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta

# ensure src package is on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.deps import get_db
from api.schemas import Token, TokenData, UserCreate, UserOut
from models.user import User
from models.role import Role
from services.auth_service import authenticate_user, create_access_token, get_password_hash, get_user, SECRET_KEY, ALGORITHM
from services.user_service import create_user as create_user_service

router = APIRouter(tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(db, token_data.username)
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def user_has_permission(user: User, code: str) -> bool:
    role = getattr(user, "role", None)
    if not role:
        return False
    perms = getattr(role, "permissions", [])
    for p in perms:
        if getattr(p, "code", None) == code:
            return True
    return False


def require_permission(code: str):
    from fastapi import Depends

    def _dep(current_user: User = Depends(get_current_active_user)) -> User:
        if not user_has_permission(current_user, code):
            raise HTTPException(status_code=403, detail="Forbidden")
        return current_user

    return _dep


@router.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/users/", response_model=UserOut, status_code=201)
def create_user(payload: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(require_permission("manage_users"))):
    existing = get_user(db, payload.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = get_password_hash(payload.password)
    return create_user_service(payload.username, hashed_password, payload.role_id, db)


@router.get("/users/me", response_model=UserOut)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user
