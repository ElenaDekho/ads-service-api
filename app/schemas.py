from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class CreateAdRequest(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    author: Optional[str] = None  # необязательное, игнорируем если есть токен


class CreateAdResponse(BaseModel):
    id: int

class GetAdResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    price: float
    author: str
    user_id: int
    created_at: Optional[datetime] = None

class UpdateAdRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    author: Optional[str] = None

class UpdateAdResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    price: float
    author: str
    user_id: int
    created_at: Optional[datetime] = None

class OKResponse(BaseModel):
    status: str = "ok"


# --- Схемы для пользователей и авторизации ---
class CreateUserRequest(BaseModel):
    username: str
    password: str
    group: str = "user"  # по умолчанию user, можно указать admin

class CreateUserResponse(BaseModel):
    id: int

class GetUserResponse(BaseModel):
    id: int
    username: str
    group: str
    created_at: Optional[datetime] = None

class UpdateUserRequest(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    group: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    token: str
