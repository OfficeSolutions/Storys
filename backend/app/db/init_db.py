from app.db.database import Base, engine
from app.models.models import Agent, Tournament, Match, Round, User, UserAgent, MoveType

# Create all tables in the database
def create_tables():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    create_tables()
    print("Database tables created successfully!")
