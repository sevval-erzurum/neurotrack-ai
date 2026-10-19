from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.db import get_db
from app.core.security import decode_access_token
from app.models import Role, User
from app.services.audit import set_actor

DB = Annotated[Session, Depends(get_db)]


def _token_from(request: Request) -> str | None:
    header = request.headers.get("Authorization", "")
    if header.lower().startswith("bearer "):
        return header[7:]
    return request.cookies.get(get_settings().cookie_name)


def current_user(request: Request, db: DB) -> User:
    token = _token_from(request)
    user_id = decode_access_token(token) if token else None
    user = db.get(User, user_id) if user_id else None
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Oturum geçersiz veya süresi dolmuş.")
    set_actor(request, user)
    return user


CurrentUser = Annotated[User, Depends(current_user)]


def require_role(*roles: Role):
    def checker(user: CurrentUser) -> User:
        if user.role not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Bu işlem için yetkiniz yok.")
        return user

    return Depends(checker)
