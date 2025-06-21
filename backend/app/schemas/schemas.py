from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class MoveType(str, Enum):
    COOPERATE = "C"
    DEFECT = "D"

# Agent Schemas
class AgentBase(BaseModel):
    name: str
    description: Optional[str] = None
    callback_url: str
    auth_token: str

class AgentCreate(AgentBase):
    pass

class AgentResponse(AgentBase):
    id: int
    api_key: str
    is_active: bool
    is_quarantined: bool
    created_at: datetime
    total_matches: int
    total_score: float
    average_score: float

    class Config:
        orm_mode = True

# Tournament Schemas
class TournamentBase(BaseModel):
    name: str
    description: Optional[str] = None
    round_count: int = 200

class TournamentCreate(TournamentBase):
    pass

class TournamentResponse(TournamentBase):
    id: int
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True

# Match Schemas
class MatchBase(BaseModel):
    tournament_id: int
    agent_a_id: int
    agent_b_id: int

class MatchCreate(MatchBase):
    pass

class RoundInfo(BaseModel):
    round_number: int
    agent_a_move: MoveType
    agent_b_move: MoveType
    agent_a_score: int
    agent_b_score: int
    agent_a_response_time: Optional[float]
    agent_b_response_time: Optional[float]

class MatchResponse(MatchBase):
    id: int
    agent_a_score: float
    agent_b_score: float
    rounds_completed: int
    is_complete: bool
    created_at: datetime
    completed_at: Optional[datetime]
    rounds: Optional[List[RoundInfo]]

    class Config:
        orm_mode = True

# Play Request/Response Schemas
class HistoryItem(BaseModel):
    self: MoveType
    opponent: MoveType

class PlayRequest(BaseModel):
    match_id: str
    round: int
    history: List[HistoryItem] = []

class PlayResponse(BaseModel):
    move: MoveType

# User Schemas
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime

    class Config:
        orm_mode = True

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
