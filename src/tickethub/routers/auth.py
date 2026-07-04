from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from tickethub.clients.dummyjson_auth import DummyJSONAuthClient
from tickethub.rate_limit import limiter
from tickethub.schemas import AuthLoginRequest, AuthTokenResponse, AuthUserResponse

router = APIRouter(prefix="/auth", tags=["auth"])

bearer_scheme = HTTPBearer(auto_error=False)


def get_bearer_token(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> str:
    # Izvlači JWT token iz Authorization headera
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nedostaje Bearer token.",
        )

    return credentials.credentials


@router.post("/login", response_model=AuthTokenResponse)
@limiter.limit("10/minute")
async def login(
    request: Request,
    login_data: AuthLoginRequest,
) -> AuthTokenResponse:
    # Prijava korisnika preko DummyJSON servisa
    try:
        async with DummyJSONAuthClient() as client:
            data = await client.login(login_data)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Neispravni korisnički podaci.",
        ) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auth servis trenutno nije dostupan.",
        ) from exc

    return AuthTokenResponse.model_validate(data)


@router.get("/me", response_model=AuthUserResponse)
@limiter.limit("60/minute")
async def get_me(
    request: Request,
    access_token: Annotated[str, Depends(get_bearer_token)],
) -> AuthUserResponse:
    # Vraća podatke prijavljenog korisnika
    try:
        async with DummyJSONAuthClient() as client:
            data = await client.get_current_user(access_token)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token nije valjan.",
        ) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auth servis trenutno nije dostupan.",
        ) from exc

    return AuthUserResponse.model_validate(data)
