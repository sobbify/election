from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.hybrid import hybrid_property
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
    is_active = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    questions = relationship("Question", back_populates="election", cascade="all, delete-orphan")
    
    @hybrid_property
    def question_count(self):
        return len(self.questions)
    
    @hybrid_property
    def candidate_count(self):
        return sum(len(q.options) for q in self.questions)
    
    @hybrid_property
    def total_votes(self):
        return sum(sum(o.votes for o in q.options) for q in self.questions)

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    image_path = Column(String, nullable=True)
    election_id = Column(Integer, ForeignKey("elections.id"), index=True)
    
    election = relationship("Election", back_populates="questions")
    options = relationship("Option", back_populates="question", cascade="all, delete-orphan")
    
    @hybrid_property
    def option_count(self):
        return len(self.options)
    
    @hybrid_property
    def total_votes(self):
        return sum(o.votes for o in self.options)

class Option(Base):
    __tablename__ = "options"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    bio = Column(String, nullable=True)
    image_path = Column(String, nullable=True)
    votes = Column(Integer, default=0, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), index=True)
    
    question = relationship("Question", back_populates="options")

# Create indexes for better query performance
__table_args__ = (
    Index('idx_election_active', Election.is_active),
    Index('idx_question_election', Question.election_id),
    Index('idx_option_question', Option.question_id),
)

def init_db():
    Base.metadata.create_all(bind=engine)
