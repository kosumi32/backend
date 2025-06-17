# Object Relational Mapping
# Write python classes that represent a sequel table

from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# What DB we want to use
engine= create_engine('sqlite:///database.db', echo=True)    # sqlite- run locally, echo=True to see SQL queries
Base = declarative_base()

# Create a class that represents a table
# Inherit from Base
class Challenge(Base):
    __tablename__ = 'challenge'

    id = Column(Integer, primary_key=True)
    difficulty= Column(String, nullable=False)
    date_created= Column(DateTime, default=datetime.now)
    created_by= Column(String, nullable=False)  # UserID of the creator
    title= Column(String, nullable=False)
    options= Column(String, nullable=False)  # JSON string of options
    correct_answer_id= Column(Integer, nullable=False)
    explanation= Column(String, nullable=True)  # Fixed spelling from explaination to explanation

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
    

class ChallengeQuota(Base):
    __tablename__ = 'challenge_quota'

    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False, unique= True)  # userID should be unique
    quota= Column(Integer, nullable=False, default= 15)  # Number of challenges created by the user
    last_reset_date= Column(DateTime, default=datetime.now)  

    def __repr__(self):
        return f"<ChallengeQuota(id={self.id}, user_id='{self.user_id}', quota={self.quota})>"
    

# Converting to SQL code
Base.metadata.create_all(engine)

# Create a session to interact with the database
Session = sessionmaker(autocommit= False, autoflush=False, bind=engine)

def get_db():
    db = Session()  # make sure dont create duplicate sessions
    try:
        yield db    # yield- generator function to return the session
    finally:
        db.close()