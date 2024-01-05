from datetime import datetime
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from src.config import Settings

from jose import jwt
from pydantic import ValidationError

from src.schema.common import TokenPayload
from src.db.session import get_db
from sqlalchemy.orm import Session
from src.repositories.users import UserRepository, PartnerRepository

reuseable_oauth = OAuth2PasswordBearer(
    tokenUrl="/api/auth/v1/verify-otp", scheme_name="JWT"
)


def get_current_user(
    token: str = Depends(reuseable_oauth), db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(
            token, Settings.JWT_SECRET_KEY, algorithms=[Settings.ALGORITHM]
        )
        # if BlockedJWT(token=token).is_blocked(db):
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="User is logged out, Login Again",
        #     )
        token_data = TokenPayload(**payload)
        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = UserRepository(db).get_user_by_phone_number(phone=token_data.sub)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token."
        )

    return user


def get_current_partner(
    token: str = Depends(reuseable_oauth), db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(
            token, Settings.PARTNER_JWT_SECRET_KEY, algorithms=[Settings.ALGORITHM]
        )
        # if BlockedJWT(token=token).is_blocked(db):
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="User is logged out, Login Again",
        #     )
        token_data = TokenPayload(**payload)
        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = PartnerRepository(db).get_partner_by_username(username=token_data.sub)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token."
        )

    return user
