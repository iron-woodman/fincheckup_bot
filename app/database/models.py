import enum
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    created_at = Column(DateTime, default=func.now())

    profile = relationship("UserProfile", back_populates="user", uselist=False)
    answers = relationship('Answer', back_populates='user')


class UserProfile(Base):
    __tablename__ = 'user_profiles'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    full_name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    city = Column(String, nullable=True)
    status_in_germany = Column(String, nullable=True)

    user = relationship("User", back_populates="profile")


class QuestionType(enum.Enum):
    SINGLE_CHOICE = "single_choice"
    MULTIPLE_CHOICE = "multiple_choice"


class Question(Base):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    question_text = Column(Text, nullable=False)
    type = Column(Enum(QuestionType), nullable=False)  # Тип вопроса
    created_at = Column(DateTime, default=func.now())

    answers = relationship('Answer', back_populates='question')
    options = relationship('AnswerOption', back_populates='question')


class Answer(Base):
    __tablename__ = 'answers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    question_id = Column(Integer, ForeignKey('questions.id'), nullable=False)
    created_at = Column(DateTime, default=func.now())

    user = relationship('User', back_populates='answers')
    question = relationship('Question', back_populates='answers')
    options = relationship('AnswerOption', back_populates='answer')


class AnswerOption(Base):
    __tablename__ = 'answer_options'

    id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(Integer, ForeignKey('questions.id'), nullable=False)
    answer_id = Column(Integer, ForeignKey('answers.id'), nullable=False) # Добавлено
    option_text = Column(Text, nullable=False)

    question = relationship('Question', back_populates='options')
    answer = relationship('Answer', back_populates='options')
