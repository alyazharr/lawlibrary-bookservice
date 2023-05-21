from datetime import datetime
import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, ExpiredSignatureError
from pydantic import BaseModel


class User(BaseModel):
    username: str
    email: str
    roles: str
    
JWT_SECRET = os.getenv('jwt_secret')
JWT_ALGORITHM = os.getenv('jwt_algo')
# Ini gatau cara masukin ke envnya guys, gw taro sini dlu aja yah

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def verify_jwt(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if datetime.fromtimestamp(payload['exp']) > datetime.now():
            return User(**payload)
    except ExpiredSignatureError:
            raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


