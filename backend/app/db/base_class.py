"""
Declarative base for all ORM models — this module ONLY defines Base.
Models import Base from here (not from db/base.py) to avoid a circular
import: models need Base, and db/base.py needs all the models.
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
