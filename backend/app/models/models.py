from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, DateTime, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

Base = declarative_base()

class MoveType(str, enum.Enum):
    COOPERATE = "C"
    DEFECT = "D"

class Agent(Base):
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text, nullable=True)
    callback_url = Column(String, nullable=False)
    auth_token = Column(String, nullable=False)
    api_key = Column(String, unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)
    is_quarantined = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    matches_as_agent_a = relationship("Match", foreign_keys="Match.agent_a_id", back_populates="agent_a")
    matches_as_agent_b = relationship("Match", foreign_keys="Match.agent_b_id", back_populates="agent_b")
    
    # Stats
    total_matches = Column(Integer, default=0)
    total_score = Column(Float, default=0.0)
    average_score = Column(Float, default=0.0)
    
    def __repr__(self):
        return f"<Agent {self.name}>"

class Tournament(Base):
    __tablename__ = "tournaments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=True)
    end_time = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    round_count = Column(Integer, default=200)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    matches = relationship("Match", back_populates="tournament")
    
    def __repr__(self):
        return f"<Tournament {self.name}>"

class Match(Base):
    __tablename__ = "matches"
    
    id = Column(Integer, primary_key=True, index=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.id"))
    agent_a_id = Column(Integer, ForeignKey("agents.id"))
    agent_b_id = Column(Integer, ForeignKey("agents.id"))
    agent_a_score = Column(Float, default=0.0)
    agent_b_score = Column(Float, default=0.0)
    rounds_completed = Column(Integer, default=0)
    is_complete = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    tournament = relationship("Tournament", back_populates="matches")
    agent_a = relationship("Agent", foreign_keys=[agent_a_id], back_populates="matches_as_agent_a")
    agent_b = relationship("Agent", foreign_keys=[agent_b_id], back_populates="matches_as_agent_b")
    rounds = relationship("Round", back_populates="match")
    
    def __repr__(self):
        return f"<Match {self.id}: {self.agent_a.name} vs {self.agent_b.name}>"

class Round(Base):
    __tablename__ = "rounds"
    
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"))
    round_number = Column(Integer, nullable=False)
    agent_a_move = Column(Enum(MoveType), nullable=False)
    agent_b_move = Column(Enum(MoveType), nullable=False)
    agent_a_score = Column(Integer, nullable=False)
    agent_b_score = Column(Integer, nullable=False)
    agent_a_response_time = Column(Float, nullable=True)  # in milliseconds
    agent_b_response_time = Column(Float, nullable=True)  # in milliseconds
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    match = relationship("Match", back_populates="rounds")
    
    def __repr__(self):
        return f"<Round {self.round_number}: {self.agent_a_move} vs {self.agent_b_move}>"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    agents = relationship("Agent", secondary="user_agents")
    
    def __repr__(self):
        return f"<User {self.email}>"

class UserAgent(Base):
    __tablename__ = "user_agents"
    
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), primary_key=True)
