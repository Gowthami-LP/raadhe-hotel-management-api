import os
from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

load_dotenv()


def _load_jwt_secret() -> str:
    secret = os.getenv("JWT_SECRET")
    if not secret or secret == "replace_with_a_long_random_secret":
        raise RuntimeError(
            "JWT_SECRET must be set to a strong, random secret in the environment"
        )
    if len(secret.encode("utf-8")) < 32:
        raise RuntimeError("JWT_SECRET must be at least 32 bytes long")
    return secret


def _load_expiration_minutes() -> int:
    try:
        expiration_minutes = int(os.getenv("JWT_EXPIRATION_MINUTES", "30"))
    except ValueError as error:
        raise RuntimeError("JWT_EXPIRATION_MINUTES must be an integer") from error
    if expiration_minutes <= 0:
        raise RuntimeError("JWT_EXPIRATION_MINUTES must be greater than zero")
    return expiration_minutes


JWT_SECRET = _load_jwt_secret()
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_MINUTES = _load_expiration_minutes()

bearer_scheme = HTTPBearer()


def create_access_token(username: str) -> str:
    expires_at = datetime.now(UTC) + timedelta(minutes=JWT_EXPIRATION_MINUTES)
    return jwt.encode(
        {"sub": username, "exp": expires_at},
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )


def require_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials,
        Depends(bearer_scheme),
    ],
) -> str:
    token = credentials.credentials
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
        )
    except jwt.ExpiredSignatureError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        ) from error
    except jwt.InvalidTokenError as error:
        raise unauthorized from error

    username = payload.get("sub")
    if not isinstance(username, str) or not username:
        raise unauthorized
    return username
