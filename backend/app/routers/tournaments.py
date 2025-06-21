from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db.database import get_db
from app.models.models import Tournament, Match, Agent
from app.schemas.schemas import TournamentCreate, TournamentResponse, MatchResponse
from app.routers.auth import get_current_active_user

router = APIRouter()

@router.post("", response_model=TournamentResponse)
async def create_tournament(
    tournament: TournamentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Create a new tournament.
    """
    db_tournament = Tournament(
        name=tournament.name,
        description=tournament.description,
        round_count=tournament.round_count,
        is_active=True
    )
    
    db.add(db_tournament)
    db.commit()
    db.refresh(db_tournament)
    
    return db_tournament

@router.get("", response_model=List[TournamentResponse])
async def get_tournaments(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    db: Session = Depends(get_db)
):
    """
    Get a list of all tournaments.
    Optional filtering for active tournaments only.
    """
    query = db.query(Tournament)
    if active_only:
        query = query.filter(Tournament.is_active == True)
    
    tournaments = query.offset(skip).limit(limit).all()
    return tournaments

@router.get("/{tournament_id}", response_model=TournamentResponse)
async def get_tournament(
    tournament_id: int,
    db: Session = Depends(get_db)
):
    """
    Get details for a specific tournament by ID.
    """
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if tournament is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournament not found"
        )
    return tournament

@router.put("/{tournament_id}", response_model=TournamentResponse)
async def update_tournament(
    tournament_id: int,
    tournament_update: TournamentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Update an existing tournament's details.
    """
    db_tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if db_tournament is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournament not found"
        )
    
    # Update fields
    db_tournament.name = tournament_update.name
    db_tournament.description = tournament_update.description
    db_tournament.round_count = tournament_update.round_count
    
    db.commit()
    db.refresh(db_tournament)
    return db_tournament

@router.delete("/{tournament_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tournament(
    tournament_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Delete a tournament (or mark as inactive).
    """
    db_tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if db_tournament is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournament not found"
        )
    
    # Instead of deleting, mark as inactive
    db_tournament.is_active = False
    db.commit()
    
    return None

@router.post("/{tournament_id}/start", response_model=TournamentResponse)
async def start_tournament(
    tournament_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Start a tournament, setting its start time.
    """
    db_tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if db_tournament is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournament not found"
        )
    
    if db_tournament.start_time is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tournament has already been started"
        )
    
    # Set start time
    db_tournament.start_time = datetime.now()
    db.commit()
    db.refresh(db_tournament)
    
    return db_tournament

@router.post("/{tournament_id}/end", response_model=TournamentResponse)
async def end_tournament(
    tournament_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    End a tournament, setting its end time.
    """
    db_tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if db_tournament is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournament not found"
        )
    
    if db_tournament.start_time is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tournament has not been started yet"
        )
    
    if db_tournament.end_time is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tournament has already ended"
        )
    
    # Set end time and mark as inactive
    db_tournament.end_time = datetime.now()
    db_tournament.is_active = False
    db.commit()
    db.refresh(db_tournament)
    
    return db_tournament

@router.get("/{tournament_id}/matches", response_model=List[MatchResponse])
async def get_tournament_matches(
    tournament_id: int,
    skip: int = 0,
    limit: int = 100,
    completed_only: bool = False,
    db: Session = Depends(get_db)
):
    """
    Get all matches for a specific tournament.
    Optional filtering for completed matches only.
    """
    # Check if tournament exists
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if tournament is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournament not found"
        )
    
    # Query matches
    query = db.query(Match).filter(Match.tournament_id == tournament_id)
    if completed_only:
        query = query.filter(Match.is_complete == True)
    
    matches = query.offset(skip).limit(limit).all()
    return matches

@router.post("/{tournament_id}/schedule", status_code=status.HTTP_201_CREATED)
async def schedule_tournament_matches(
    tournament_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Schedule matches for a tournament using round-robin format.
    Only non-quarantined and active agents will participate.
    """
    # Check if tournament exists
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if tournament is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournament not found"
        )
    
    # Get eligible agents
    eligible_agents = db.query(Agent).filter(
        Agent.is_active == True,
        Agent.is_quarantined == False
    ).all()
    
    if len(eligible_agents) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Need at least 2 eligible agents to schedule matches"
        )
    
    # Schedule round-robin matches
    matches_created = 0
    for i in range(len(eligible_agents)):
        for j in range(i + 1, len(eligible_agents)):
            agent_a = eligible_agents[i]
            agent_b = eligible_agents[j]
            
            # Create match
            match = Match(
                tournament_id=tournament_id,
                agent_a_id=agent_a.id,
                agent_b_id=agent_b.id,
                is_complete=False,
                rounds_completed=0
            )
            
            db.add(match)
            matches_created += 1
    
    db.commit()
    
    return {"message": f"Successfully scheduled {matches_created} matches"}
