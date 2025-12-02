from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase # New


# Строка подключения для SQLite
DATABASE_URL = "sqlite:///../ecommerce.db"

# Создаём Engine
engine = create_engine(DATABASE_URL, echo=True)

# Настраиваем фабрику сеансов
SessionLocal = sessionmaker(bind=engine)


# Определяем базовый класс для моделей
class Base(DeclarativeBase):  # New
    pass
