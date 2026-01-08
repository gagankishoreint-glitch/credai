from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import create_access_token, verify_password, get_password_hash
from app.api.deps import MOCK_USERS

router = APIRouter()

@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = MOCK_USERS.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
        
    # In Mock, password = username for simplicity, or hardcoded 'secret'
    # Let's say password is 'secret' for everyone for MVP
    if form_data.password != "secret":
        raise HTTPException(status_code=400, detail="Incorrect password")
        
    access_token = create_access_token(subject=user_dict["username"])
    return {"access_token": access_token, "token_type": "bearer"}
