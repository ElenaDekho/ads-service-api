from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from config import config

# Создаём асинхронный движок
engine = create_async_engine(config.DATABASE_URL, echo=True)

# Создаём фабрику сессий
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Базовый класс для моделей
from sqlalchemy.orm import declarative_base
Base = declarative_base()


# Функция для получения сессии (нужна для auth.py)
async def get_db_session():
    async with AsyncSessionLocal() as session:
        yield session