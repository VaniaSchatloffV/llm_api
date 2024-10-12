from fastapi import Depends, HTTPException
from fastapi.security import OAuth2AuthorizationCodeBearer
from authlib.jose import jwt, JsonWebKey
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
        jwks = JsonWebKey.import_key_set(response.json())
        unverified_header = jwt.decode_header(token)
        key = jwks.find_by_kid(unverified_header['kid'])
        if key:
            payload = jwt.decode(token, key, claims_params={
                'aud': API_IDENTIFIER,
                'iss': f"https://{AUTH0_DOMAIN}/"
            })
            return payload
        
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=403, detail="Token verification failed")
