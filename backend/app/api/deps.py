from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.security import decode_token
from pydantic import BaseModel

class User(BaseModel):
    username: str
    role: str # 'admin', 'underwriter', 'applicant'
    disabled: Optional[bool] = False

# MOCK DB
MOCK_USERS = {
    "admin": {"username": "admin", "role": "admin"},
    "underwriter_1": {"username": "underwriter_1", "role": "underwriter"},
    "applicant_001": {"username": "applicant_001", "role": "applicant"}
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    username = decode_token(token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_dict = MOCK_USERS.get(username)
    if not user_dict:
        raise HTTPException(status_code=404, detail="User not found")
        
    user = User(**user_dict)
    if user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user

class RoleChecker:
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)):
        if user.role not in self.allowed_roles:
            raise HTTPException(status_code=403, detail="Operation not permitted")
        return user
