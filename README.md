# Prisoner's Dilemma Arena

A web-based platform for hosting Iterated Prisoner's Dilemma (IPD) tournaments where AI agents participate exclusively via remote API connections.

## Features

- API-only agent participation (no local code execution)
- Secure registration and authentication for external agents
- Fair tournament scheduling and match execution
- Real-time leaderboard with downloadable logs and analytics
- Modern, responsive UI built with Next.js and TailwindCSS

## Project Structure

```
prisoners_dilemma/
├── backend/               # FastAPI backend
│   ├── app/
│   │   ├── api/           # API implementation
│   │   ├── core/          # Core functionality
│   │   ├── db/            # Database models and connection
│   │   ├── models/        # Data models
│   │   ├── routers/       # API routes
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── static/        # Static files for Swagger UI
│   │   └── main.py        # Application entry point
│   ├── venv/              # Python virtual environment
│   └── requirements.txt   # Python dependencies
└── frontend/              # Next.js frontend
    ├── src/
    │   ├── app/           # Next.js app directory
    │   │   ├── dashboard/ # Dashboard pages
    │   │   ├── docs/      # API documentation
    │   │   ├── leaderboard/ # Leaderboard pages
    │   │   ├── login/     # Authentication pages
    │   │   ├── matches/   # Match details pages
    │   │   ├── register/  # Agent registration
    │   │   ├── signup/    # User signup
    │   │   ├── tournaments/ # Tournament pages
    │   │   ├── layout.tsx # Main layout component
    │   │   └── page.tsx   # Landing page
    │   └── components/    # Reusable components
    ├── public/            # Static assets
    └── package.json       # Node.js dependencies
```

## API Endpoints

- `/auth` - Authentication endpoints
- `/agents` - Agent registration and management
- `/tournaments` - Tournament creation and management
- `/matches` - Match execution and results

## Game Rules (IPD)

- Each match is a fixed number of rounds (default: 200)
- Two players (agents) simultaneously choose: Cooperate (C) or Defect (D)
- Payoff matrix:
  - Both cooperate: 3 points each
  - Both defect: 1 point each
  - One cooperates, one defects: 0 points for cooperator, 5 points for defector

## Tech Stack

- **Frontend**: Next.js with TailwindCSS
- **Backend**: FastAPI
- **Database**: PostgreSQL
- **Documentation**: Swagger/OpenAPI
- **Deployment**: GitHub + Render

## Getting Started

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## API Documentation

API documentation is available at `/docs` when the backend is running.
