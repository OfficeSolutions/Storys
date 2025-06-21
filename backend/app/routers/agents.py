from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List, Optional
import secrets
import string

from app.db.database import get_db
from app.models.models import Agent
from app.schemas.schemas import AgentCreate, AgentResponse
from app.routers.auth import get_current_active_user

router = APIRouter()

# Helper function to generate API key
def generate_api_key(length=32):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

@router.post("/register", response_model=AgentResponse)
async def register_agent(
    agent: AgentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Register a new agent with a callback URL and authentication token.
    Returns the agent details including a generated API key.
    """
    # Check if agent name already exists
    db_agent = db.query(Agent).filter(Agent.name == agent.name).first()
    if db_agent:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agent with this name already exists"
        )
    
    # Generate API key
    api_key = generate_api_key()
    
    # Create new agent
    db_agent = Agent(
        name=agent.name,
        description=agent.description,
        callback_url=agent.callback_url,
        auth_token=agent.auth_token,
        api_key=api_key,
        is_active=True,
        is_quarantined=True  # New agents start in quarantine
    )
    
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    
    return db_agent

@router.get("", response_model=List[AgentResponse])
async def get_agents(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Get a list of all registered agents.
    Optional filtering for active agents only.
    """
    query = db.query(Agent)
    if active_only:
        query = query.filter(Agent.is_active == True)
    
    agents = query.offset(skip).limit(limit).all()
    return agents

@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Get details for a specific agent by ID.
    """
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    return agent

@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: int,
    agent_update: AgentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Update an existing agent's details.
    """
    db_agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if db_agent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Update fields
    db_agent.name = agent_update.name
    db_agent.description = agent_update.description
    db_agent.callback_url = agent_update.callback_url
    db_agent.auth_token = agent_update.auth_token
    
    db.commit()
    db.refresh(db_agent)
    return db_agent

@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Delete an agent (or mark as inactive).
    """
    db_agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if db_agent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Instead of deleting, mark as inactive
    db_agent.is_active = False
    db.commit()
    
    return None

@router.get("/{agent_id}/stats", response_model=AgentResponse)
async def get_agent_stats(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Get detailed statistics for a specific agent.
    """
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Agent stats are already included in the AgentResponse model
    return agent

@router.post("/{agent_id}/toggle-quarantine", response_model=AgentResponse)
async def toggle_agent_quarantine(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Toggle an agent's quarantine status.
    """
    db_agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if db_agent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Toggle quarantine status
    db_agent.is_quarantined = not db_agent.is_quarantined
    db.commit()
    db.refresh(db_agent)
    
    return db_agent

@router.post("/{agent_id}/regenerate-key", response_model=AgentResponse)
async def regenerate_api_key(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Regenerate the API key for an agent.
    """
    db_agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if db_agent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Generate new API key
    db_agent.api_key = generate_api_key()
    db.commit()
    db.refresh(db_agent)
    
    return db_agent
