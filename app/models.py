from sqlalchemy import Column, Integer, String, Float, DateTime, func
from database import Base
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, func
from database import Base


# --- НОВАЯ МОДЕЛЬ ПОЛЬЗОВАТЕЛЯ ---
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password = Column(String(100), nullable=False)  # хэш пароля
    group = Column(String(20), nullable=False, default="user")  # user или admin
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Advertisement(Base):
    __tablename__ = "advertisements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    author = Column(String(100), nullable=False)
    user_id = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "price": self.price,
            "author": self.author,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# --- Модель для хранения токенов ---
class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)