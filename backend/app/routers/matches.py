from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import requests
import json
import asyncio
import time

from app.db.database import get_db
from app.models.models import Match, Round, Agent, Tournament, MoveType
from app.schemas.schemas import MatchCreate, MatchResponse, PlayRequest, PlayResponse, HistoryItem
from app.routers.auth import get_current_active_user

router = APIRouter()

# Payoff matrix for Prisoner's Dilemma
PAYOFF_MATRIX = {
    # (agent_a_move, agent_b_move): (agent_a_score, agent_b_score)
    (MoveType.COOPERATE, MoveType.COOPERATE): (3, 3),
    (MoveType.COOPERATE, MoveType.DEFECT): (0, 5),
    (MoveType.DEFECT, MoveType.COOPERATE): (5, 0),
    (MoveType.DEFECT, MoveType.DEFECT): (1, 1)
}

@router.post("", response_model=MatchResponse)
async def create_match(
    match: MatchCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Create a new match between two agents.
    """
    # Check if tournament exists
    tournament = db.query(Tournament).filter(Tournament.id == match.tournament_id).first()
    if tournament is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournament not found"
        )
    
    # Check if agents exist
    agent_a = db.query(Agent).filter(Agent.id == match.agent_a_id).first()
    agent_b = db.query(Agent).filter(Agent.id == match.agent_b_id).first()
    
    if agent_a is None or agent_b is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or both agents not found"
        )
    
    # Create match
    db_match = Match(
        tournament_id=match.tournament_id,
        agent_a_id=match.agent_a_id,
        agent_b_id=match.agent_b_id,
        is_complete=False,
        rounds_completed=0
    )
    
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    
    return db_match

@router.get("", response_model=List[MatchResponse])
async def get_matches(
    skip: int = 0,
    limit: int = 100,
    tournament_id: Optional[int] = None,
    agent_id: Optional[int] = None,
    completed_only: bool = False,
    db: Session = Depends(get_db)
):
    """
    Get a list of matches with optional filtering.
    """
    query = db.query(Match)
    
    if tournament_id:
        query = query.filter(Match.tournament_id == tournament_id)
    
    if agent_id:
        query = query.filter((Match.agent_a_id == agent_id) | (Match.agent_b_id == agent_id))
    
    if completed_only:
        query = query.filter(Match.is_complete == True)
    
    matches = query.offset(skip).limit(limit).all()
    return matches

@router.get("/{match_id}", response_model=MatchResponse)
async def get_match(
    match_id: int,
    include_rounds: bool = False,
    db: Session = Depends(get_db)
):
    """
    Get details for a specific match by ID.
    Optionally include round details.
    """
    match = db.query(Match).filter(Match.id == match_id).first()
    if match is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )
    
    # Include rounds if requested
    if include_rounds:
        rounds = db.query(Round).filter(Round.match_id == match_id).order_by(Round.round_number).all()
        match.rounds = rounds
    
    return match

@router.post("/{match_id}/run", status_code=status.HTTP_202_ACCEPTED)
async def run_match(
    match_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Run a match in the background.
    """
    match = db.query(Match).filter(Match.id == match_id).first()
    if match is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )
    
    if match.is_complete:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Match is already complete"
        )
    
    # Get tournament for round count
    tournament = db.query(Tournament).filter(Tournament.id == match.tournament_id).first()
    if tournament is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournament not found"
        )
    
    # Schedule match execution in background
    background_tasks.add_task(
        execute_match,
        match_id=match_id,
        round_count=tournament.round_count,
        db_session=db
    )
    
    return {"message": f"Match {match_id} scheduled for execution"}

async def execute_match(match_id: int, round_count: int, db_session: Session):
    """
    Execute a match between two agents.
    This runs in the background and updates the database as rounds are completed.
    """
    # Get match details
    match = db_session.query(Match).filter(Match.id == match_id).first()
    if match is None or match.is_complete:
        return
    
    # Get agents
    agent_a = db_session.query(Agent).filter(Agent.id == match.agent_a_id).first()
    agent_b = db_session.query(Agent).filter(Agent.id == match.agent_b_id).first()
    
    if agent_a is None or agent_b is None:
        return
    
    # Initialize scores
    agent_a_total_score = 0
    agent_b_total_score = 0
    
    # Get existing rounds if any
    existing_rounds = db_session.query(Round).filter(Round.match_id == match_id).order_by(Round.round_number).all()
    start_round = len(existing_rounds)
    
    # Prepare history for both agents
    history_a = []
    history_b = []
    
    # Add existing rounds to history
    for round_obj in existing_rounds:
        history_a.append({
            "self": round_obj.agent_a_move,
            "opponent": round_obj.agent_b_move
        })
        history_b.append({
            "self": round_obj.agent_b_move,
            "opponent": round_obj.agent_a_move
        })
        
        agent_a_total_score += round_obj.agent_a_score
        agent_b_total_score += round_obj.agent_b_score
    
    # Run remaining rounds
    for round_num in range(start_round, round_count):
        # Prepare requests for both agents
        request_a = {
            "match_id": str(match_id),
            "round": round_num,
            "history": history_a
        }
        
        request_b = {
            "match_id": str(match_id),
            "round": round_num,
            "history": history_b
        }
        
        # Get moves from agents (with timeout)
        agent_a_move, agent_a_time = await get_agent_move(agent_a, request_a)
        agent_b_move, agent_b_time = await get_agent_move(agent_b, request_b)
        
        # Calculate scores based on payoff matrix
        agent_a_score, agent_b_score = PAYOFF_MATRIX.get(
            (agent_a_move, agent_b_move),
            (1, 1)  # Default if something goes wrong
        )
        
        # Update history
        history_a.append({
            "self": agent_a_move,
            "opponent": agent_b_move
        })
        history_b.append({
            "self": agent_b_move,
            "opponent": agent_a_move
        })
        
        # Update total scores
        agent_a_total_score += agent_a_score
        agent_b_total_score += agent_b_score
        
        # Create round record
        round_obj = Round(
            match_id=match_id,
            round_number=round_num,
            agent_a_move=agent_a_move,
            agent_b_move=agent_b_move,
            agent_a_score=agent_a_score,
            agent_b_score=agent_b_score,
            agent_a_response_time=agent_a_time,
            agent_b_response_time=agent_b_time
        )
        
        db_session.add(round_obj)
        
        # Update match progress
        match.rounds_completed = round_num + 1
        db_session.commit()
    
    # Mark match as complete
    match.is_complete = True
    match.agent_a_score = agent_a_total_score
    match.agent_b_score = agent_b_total_score
    match.completed_at = datetime.now()
    
    # Update agent stats
    agent_a.total_matches += 1
    agent_a.total_score += agent_a_total_score
    agent_a.average_score = agent_a.total_score / agent_a.total_matches
    
    agent_b.total_matches += 1
    agent_b.total_score += agent_b_total_score
    agent_b.average_score = agent_b.total_score / agent_b.total_matches
    
    db_session.commit()

async def get_agent_move(agent, request_data):
    """
    Get a move from an agent with timeout.
    Returns the move and response time in milliseconds.
    Defaults to DEFECT if timeout or error.
    """
    start_time = time.time()
    try:
        # Set timeout to 200ms as per spec
        timeout = 0.2  # seconds
        
        # Prepare headers with auth token
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {agent.auth_token}"
        }
        
        # Make request to agent's callback URL
        response = requests.post(
            agent.callback_url,
            headers=headers,
            data=json.dumps(request_data),
            timeout=timeout
        )
        
        end_time = time.time()
        response_time = (end_time - start_time) * 1000  # convert to ms
        
        if response.status_code == 200:
            response_data = response.json()
            move = response_data.get("move", MoveType.DEFECT)
            
            # Validate move
            if move not in [MoveType.COOPERATE, MoveType.DEFECT]:
                move = MoveType.DEFECT
                
            return move, response_time
        else:
            return MoveType.DEFECT, response_time
            
    except (requests.RequestException, json.JSONDecodeError, KeyError):
        end_time = time.time()
        response_time = (end_time - start_time) * 1000  # convert to ms
        return MoveType.DEFECT, response_time
