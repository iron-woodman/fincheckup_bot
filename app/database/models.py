import enum
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
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
    user_answer_options = relationship('UserAnswerOptions', back_populates='user')


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

    user_answer_options = relationship('UserAnswerOptions', back_populates='question')
    options = relationship('AnswerOption', back_populates='question')


class UserAnswerOptions(Base):
    __tablename__ = 'user_answer_options'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    question_id = Column(Integer, ForeignKey('questions.id'), nullable=False)
    answer_option_id = Column(Integer, ForeignKey('answer_options.id'), nullable=False)
    created_at = Column(DateTime, default=func.now())

    user = relationship('User', back_populates='user_answer_options')
    question = relationship('Question', back_populates='user_answer_options')
    answer_option = relationship('AnswerOption', back_populates='user_answer_options')


class AnswerOption(Base):
    __tablename__ = 'answer_options'

    id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(Integer, ForeignKey('questions.id'), nullable=False)
    option_text = Column(Text, nullable=False)

    question = relationship('Question', back_populates='options')
    user_answer_options = relationship('UserAnswerOptions', back_populates='answer_option')
