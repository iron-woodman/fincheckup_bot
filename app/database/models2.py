from sqlalchemy import (Column, Integer, String, Text, DateTime, Boolean, ForeignKey, TIMESTAMP,
                        Identity, BigInteger, Date, Enum)
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
import enum
from datetime import datetime

# from app.database.database import get_async_session


class Base(AsyncAttrs, DeclarativeBase):
    pass


class MarriageStatus(enum.Enum):
    LEDIG = "Ledig"
    VERHEIRATET = "Verheiratet"
    GESCHIEDEN = "Geschieden"
    VERWITWET = "Verwitwet"


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at = Column(DateTime, default=datetime.now)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    is_admin = Column(Boolean, default=False)
    user_answers = relationship("UserAnswer", back_populates="user")
    profile = relationship("UserProfile", back_populates="user", uselist=False)


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    first_name: Mapped[str] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str] = mapped_column(String(255), nullable=True)
    birth_date: Mapped[Date] = mapped_column(Date, nullable=True)
    marriage_status: Mapped[MarriageStatus] = mapped_column(Enum(MarriageStatus), nullable=True)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=True)
    email: Mapped[str] = mapped_column(String(255), nullable=True)
    children_under_18: Mapped[int] = mapped_column(Integer, nullable=True)

    user = relationship("User", back_populates="profile")


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, Identity(), primary_key=True)
    text = Column(Text)

    options = relationship("Option", back_populates="question")
    user_answers = relationship("UserAnswer", back_populates="question")


class Option(Base):
    __tablename__ = "options"

    id = Column(Integer, Identity(), primary_key=True)
    question_id = Column(Integer, ForeignKey("questions.id"))
    text = Column(Text)

    question = relationship("Question", back_populates="options")
    user_answers = relationship("UserAnswer", back_populates="option")


class UserAnswer(Base):
    __tablename__ = "user_answers"

    id = Column(Integer, Identity(), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    option_id = Column(Integer, ForeignKey("options.id"))
    created_at = Column(TIMESTAMP, server_default=func.now())

    question = relationship("Question", back_populates="user_answers")
    option = relationship("Option", back_populates="user_answers")
    user = relationship("User", back_populates="user_answers")



# async def async_main():
#     async with get_async_session(). async_engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)