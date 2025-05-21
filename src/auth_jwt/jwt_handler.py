from datetime import datetime, timedelta
from typing import Optional
import jwt
from fastapi.security import OAuth2PasswordBearer
from settings import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_ACCESS_TOKEN_EXPIRE_MINUTES
from adapters.connector import put_cache_data, get_cache_data, delete_cache_data

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    put_cache_data(
        f"token:{encoded_jwt}",
        str(to_encode["user_id"]),
        int(expires_delta.total_seconds() if expires_delta else JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    )
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    try:
        if not get_cache_data(f"token:{token}"):
            return None
        
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
            
        user_id = payload["user_id"]
        if user_id is None:
            return None
        return payload
    except jwt.PyJWTError:
        return None

def revoke_token(token: str):
    delete_cache_data(f"token:{token}")