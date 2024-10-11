from fastapi import Depends, HTTPException
from fastapi.security import OAuth2AuthorizationCodeBearer
from jose import JWTError, jwt
from pydantic import BaseModel

import requests

from app.dependencies import get_settings

settings = get_settings()


AUTH0_DOMAIN = settings.auth0_domain
API_IDENTIFIER = settings.api_identifier
AUTH0_CLIENT_ID = settings.auth0_client_id
AUTH0_CLIENT_SECRET = settings.auth0_client_secret
ALGORITHM = settings.algorithm

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"https://{AUTH0_DOMAIN}/authorize",
    tokenUrl=f"https://{AUTH0_DOMAIN}/oauth/token"
)

class TokenData(BaseModel):
    sub: str = None

async def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        if settings.environment == "dev":
            return {"sub": "development_user"}
        response = requests.get(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
        jwks = response.json()
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
        if rsa_key:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=[ALGORITHM],
                audience=API_IDENTIFIER,
                issuer=f"https://{AUTH0_DOMAIN}/"
            )
            return payload
        raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=403, detail="Token verification failed")
