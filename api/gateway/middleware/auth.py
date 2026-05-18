# api/gateway/middleware/auth.py
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Request

class AuthMiddleware:
    """JWT tabanlı kimlik doğrulama."""
    
    def __init__(self, secret_key: str, token_expiry: int = 86400):
        self.secret_key = secret_key
        self.token_expiry = token_expiry
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def create_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(seconds=self.token_expiry)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm="HS256")
    
    def verify_token(self, token: str) -> Optional[dict]:
        try:
            return jwt.decode(token, self.secret_key, algorithms=["HS256"])
        except JWTError:
            return None
    
    async def authenticate(self, request: Request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Geçersiz kimlik doğrulama")
        
        token = auth_header.split(" ")[1]
        payload = self.verify_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Token geçersiz veya süresi dolmuş")
        
        return payload