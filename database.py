from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, DateTime, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, timezone

SQLALCHEMY_DATABASE_URL = "sqlite:///./election.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Election(Base):
    __tablename__ = "elections"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    questions = relationship("Question", back_populates="election", cascade="all, delete-orphan")

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    image_data = Column(LargeBinary, nullable=True)
    image_type = Column(String, nullable=True)
    election_id = Column(Integer, ForeignKey("elections.id"))
    
    election = relationship("Election", back_populates="questions")
    options = relationship("Option", back_populates="question", cascade="all, delete-orphan")

class Option(Base):
    __tablename__ = "options"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    bio = Column(String, nullable=True)
    image_data = Column(LargeBinary, nullable=True)
    image_type = Column(String, nullable=True)
    votes = Column(Integer, default=0)
    question_id = Column(Integer, ForeignKey("questions.id"))
    
    question = relationship("Question", back_populates="options")

def init_db():
    Base.metadata.create_all(bind=engine)
