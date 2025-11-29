from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = "sqlite+aiosqlite:///./realty_bot.db"

engine = create_async_engine(DATABASE_URL, echo=False)

#Фабрика сессей - отсюда будем брать сессию в каждом хендлере
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Базовый класс для моделей
class Base(DeclarativeBase):
    pass