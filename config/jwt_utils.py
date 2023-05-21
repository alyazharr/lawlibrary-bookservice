from datetime import datetime
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, ExpiredSignatureError
from pydantic import BaseModel


class User(BaseModel):
    username: str
    email: str
    roles: str


# Ini gatau cara masukin ke envnya guys, gw taro sini dlu aja yah
JWT_SECRET = "ca8b5e457ae049f68350597a199b2ad81fb9fb78ae7102bbfb349326d0ea7a464421323c3eac27f9209c5fe6ff2f0612a52dd40d2f663d1e311a5ec3e95ab547"
JWT_ALGORITHM = "HS256"
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


