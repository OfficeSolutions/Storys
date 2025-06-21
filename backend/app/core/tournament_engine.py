import asyncio
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from app.db.database import SessionLocal
from app.models.models import Tournament, Match, Agent, Round, MoveType
from app.routers.matches import execute_match

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class TournamentEngine:
    """
    Tournament Engine for scheduling and running Prisoner's Dilemma tournaments.
    """
    
    def __init__(self):
        self.running_tournaments = set()
    
    async def schedule_tournament(self, tournament_id: int, matchmaking_type: str = "round_robin"):
        """
        Schedule matches for a tournament.
        
        Args:
            tournament_id: ID of the tournament to schedule
            matchmaking_type: Type of matchmaking ("round_robin" or "elo")
        """
        logger.info(f"Scheduling tournament {tournament_id} with {matchmaking_type} matchmaking")
        
        db = SessionLocal()
        try:
            # Get tournament
            tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
            if not tournament:
                logger.error(f"Tournament {tournament_id} not found")
                return False
            
            # Get eligible agents (active and not quarantined)
            eligible_agents = db.query(Agent).filter(
                Agent.is_active == True,
                Agent.is_quarantined == False
            ).all()
            
            if len(eligible_agents) < 2:
                logger.error(f"Not enough eligible agents for tournament {tournament_id}")
                return False
            
            # Schedule matches based on matchmaking type
            if matchmaking_type == "round_robin":
                await self._schedule_round_robin(db, tournament, eligible_agents)
            elif matchmaking_type == "elo":
                await self._schedule_elo_based(db, tournament, eligible_agents)
            else:
                logger.error(f"Unknown matchmaking type: {matchmaking_type}")
                return False
            
            # Update tournament start time
            tournament.start_time = datetime.now()
            db.commit()
            
            logger.info(f"Tournament {tournament_id} scheduled successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error scheduling tournament {tournament_id}: {str(e)}")
            db.rollback()
            return False
        finally:
            db.close()
    
    async def _schedule_round_robin(self, db: Session, tournament: Tournament, agents: List[Agent]):
        """
        Schedule round-robin matches where each agent plays against all others.
        """
        matches_created = 0
        
        for i in range(len(agents)):
            for j in range(i + 1, len(agents)):
                agent_a = agents[i]
                agent_b = agents[j]
                
                # Create match
                match = Match(
                    tournament_id=tournament.id,
                    agent_a_id=agent_a.id,
                    agent_b_id=agent_b.id,
                    is_complete=False,
                    rounds_completed=0
                )
                
                db.add(match)
                matches_created += 1
        
        db.commit()
        logger.info(f"Created {matches_created} round-robin matches for tournament {tournament.id}")
    
    async def _schedule_elo_based(self, db: Session, tournament: Tournament, agents: List[Agent]):
        """
        Schedule matches based on Elo ratings (agents with similar scores play each other).
        """
        # Sort agents by average score
        agents.sort(key=lambda a: a.average_score if a.average_score is not None else 0, reverse=True)
        
        matches_created = 0
        
        # Match agents with similar ratings
        for i in range(len(agents)):
            # Each agent plays against 2-3 others with similar ratings
            for j in range(1, min(4, len(agents))):
                opponent_idx = (i + j) % len(agents)
                agent_a = agents[i]
                agent_b = agents[opponent_idx]
                
                # Create match
                match = Match(
                    tournament_id=tournament.id,
                    agent_a_id=agent_a.id,
                    agent_b_id=agent_b.id,
                    is_complete=False,
                    rounds_completed=0
                )
                
                db.add(match)
                matches_created += 1
        
        db.commit()
        logger.info(f"Created {matches_created} Elo-based matches for tournament {tournament.id}")
    
    async def run_tournament(self, tournament_id: int, concurrent_matches: int = 5):
        """
        Run all matches in a tournament.
        
        Args:
            tournament_id: ID of the tournament to run
            concurrent_matches: Number of matches to run concurrently
        """
        logger.info(f"Starting tournament {tournament_id} with {concurrent_matches} concurrent matches")
        
        if tournament_id in self.running_tournaments:
            logger.warning(f"Tournament {tournament_id} is already running")
            return False
        
        self.running_tournaments.add(tournament_id)
        
        try:
            db = SessionLocal()
            
            # Get tournament
            tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
            if not tournament:
                logger.error(f"Tournament {tournament_id} not found")
                self.running_tournaments.remove(tournament_id)
                return False
            
            # Get all pending matches
            pending_matches = db.query(Match).filter(
                Match.tournament_id == tournament_id,
                Match.is_complete == False
            ).all()
            
            if not pending_matches:
                logger.warning(f"No pending matches found for tournament {tournament_id}")
                self._complete_tournament(db, tournament)
                self.running_tournaments.remove(tournament_id)
                return True
            
            # Run matches in batches
            total_matches = len(pending_matches)
            completed = 0
            
            logger.info(f"Running {total_matches} matches for tournament {tournament_id}")
            
            # Process matches in batches
            for i in range(0, total_matches, concurrent_matches):
                batch = pending_matches[i:i+concurrent_matches]
                tasks = []
                
                for match in batch:
                    # Create a new session for each match
                    match_session = SessionLocal()
                    tasks.append(
                        execute_match(
                            match_id=match.id,
                            round_count=tournament.round_count,
                            db_session=match_session
                        )
                    )
                
                # Wait for all matches in this batch to complete
                await asyncio.gather(*tasks)
                completed += len(batch)
                logger.info(f"Completed {completed}/{total_matches} matches for tournament {tournament_id}")
            
            # Check if all matches are complete
            incomplete_count = db.query(Match).filter(
                Match.tournament_id == tournament_id,
                Match.is_complete == False
            ).count()
            
            if incomplete_count == 0:
                self._complete_tournament(db, tournament)
                logger.info(f"Tournament {tournament_id} completed successfully")
            else:
                logger.warning(f"Tournament {tournament_id} has {incomplete_count} incomplete matches")
            
            return True
            
        except Exception as e:
            logger.error(f"Error running tournament {tournament_id}: {str(e)}")
            return False
        finally:
            if tournament_id in self.running_tournaments:
                self.running_tournaments.remove(tournament_id)
            db.close()
    
    def _complete_tournament(self, db: Session, tournament: Tournament):
        """
        Mark a tournament as complete and update end time.
        """
        tournament.is_active = False
        tournament.end_time = datetime.now()
        db.commit()
    
    async def get_tournament_status(self, tournament_id: int):
        """
        Get the current status of a tournament.
        """
        db = SessionLocal()
        try:
            tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
            if not tournament:
                return {"error": "Tournament not found"}
            
            total_matches = db.query(func.count(Match.id)).filter(
                Match.tournament_id == tournament_id
            ).scalar()
            
            completed_matches = db.query(func.count(Match.id)).filter(
                Match.tournament_id == tournament_id,
                Match.is_complete == True
            ).scalar()
            
            return {
                "tournament_id": tournament_id,
                "name": tournament.name,
                "is_active": tournament.is_active,
                "start_time": tournament.start_time,
                "end_time": tournament.end_time,
                "total_matches": total_matches,
                "completed_matches": completed_matches,
                "progress": f"{completed_matches}/{total_matches}",
                "percent_complete": (completed_matches / total_matches * 100) if total_matches > 0 else 0
            }
        finally:
            db.close()
    
    async def get_leaderboard(self, tournament_id: Optional[int] = None, timeframe: str = "all"):
        """
        Get the leaderboard of agents.
        
        Args:
            tournament_id: Optional tournament ID to filter results
            timeframe: Time period for the leaderboard ("daily", "weekly", "all")
        """
        db = SessionLocal()
        try:
            query = db.query(Agent)
            
            # Filter by active agents
            query = query.filter(Agent.is_active == True)
            
            # Apply timeframe filter if needed
            if timeframe == "daily":
                yesterday = datetime.now() - timedelta(days=1)
                query = query.filter(Agent.updated_at >= yesterday)
            elif timeframe == "weekly":
                last_week = datetime.now() - timedelta(days=7)
                query = query.filter(Agent.updated_at >= last_week)
            
            # Get agents and sort by average score
            agents = query.all()
            agents.sort(key=lambda a: a.average_score if a.average_score is not None else 0, reverse=True)
            
            # Format results
            results = []
            for i, agent in enumerate(agents):
                results.append({
                    "rank": i + 1,
                    "id": agent.id,
                    "name": agent.name,
                    "total_matches": agent.total_matches,
                    "total_score": agent.total_score,
                    "average_score": agent.average_score
                })
            
            return results
        finally:
            db.close()

# Create a singleton instance
tournament_engine = TournamentEngine()
