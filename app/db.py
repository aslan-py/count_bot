"""Используем синхронную версию sqlalchemy."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.constants import ModelsSettings

engine = create_engine(ModelsSettings.DATABASE_URL)
SessionLocal = sessionmaker(engine, expire_on_commit=False)
