from datetime import datetime, timedelta
from typing import Union, Any
from jose import jwt
from src.config import settings


def create_access_token(
    subject: Union[str, Any], expires_delta=None, secret_key=None
) -> str:
    if secret_key is None:
        secret_key = settings.JWT_SECRET_KEY
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, secret_key, settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(
    subject: Union[str, Any], expires_delta=None, secret_key=None
) -> str:
    if secret_key is None:
        secret_key = settings.JWT_REFRESH_SECRET_KEY
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(
            minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, secret_key, settings.ALGORITHM)
    return encoded_jwt
