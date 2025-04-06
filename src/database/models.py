from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, func, Table, Enum as SqlEnum
from sqlalchemy.orm import relationship, mapped_column, Mapped, DeclarativeBase
from sqlalchemy.sql.schema import ForeignKey, PrimaryKeyConstraint
from sqlalchemy.sql.sqltypes import DateTime
from src.schemas import UserRole

class Base(DeclarativeBase):
    pass

class Contact(Base):
    __tablename__ = "contacts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    firstname: Mapped[str] = mapped_column(String(50), nullable=False)
    lastname: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(16), nullable=False)
    birthday: Mapped[str] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        "created_at", DateTime, default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        "updated_at", DateTime, default=func.now(), onupdate=func.now()
    )
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    done: Mapped[bool] = mapped_column(Boolean, default=False)
    user_id = Column(
        "user_id", ForeignKey("users.id", ondelete="CASCADE"), default=None
    )
    user = relationship("User", backref="notes")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    role = Column(SqlEnum(UserRole), default=UserRole.USER, nullable=False)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=func.now())
    avatar = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)
    refresh_token = Column(String, nullable=True)
