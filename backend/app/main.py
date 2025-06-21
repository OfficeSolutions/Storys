from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # DON'T CHANGE THIS !!!

# Create FastAPI app
app = FastAPI(
    title="Prisoner's Dilemma Arena",
    description="API for Iterated Prisoner's Dilemma tournaments",
    version="1.0.0",
    docs_url=None,  # Disable default docs
    redoc_url=None  # Disable default redoc
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to the Prisoner's Dilemma Arena API",
        "version": "1.0.0",
        "documentation": "/docs"
    }

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}

# Custom Swagger UI
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html(request: Request):
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )

# Custom ReDoc
@app.get("/redoc", include_in_schema=False)
async def redoc_html(request: Request):
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - ReDoc",
        redoc_js_url="/static/redoc.standalone.js",
    )

# Import and include routers
from app.routers import agents, tournaments, matches, auth

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(agents.router, prefix="/agents", tags=["Agents"])
app.include_router(tournaments.router, prefix="/tournaments", tags=["Tournaments"])
app.include_router(matches.router, prefix="/matches", tags=["Matches"])

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
