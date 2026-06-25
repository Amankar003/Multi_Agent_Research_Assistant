"""
main.py — The FastAPI Backend
==============================
This file creates a web server with ONE endpoint:
  POST /research  →  takes a topic, runs the 3-agent pipeline, returns the report

FastAPI is a Python web framework (like Flask, but faster).
It automatically creates API documentation at http://localhost:8000/docs

"Endpoint" = a URL that your app listens on and responds to.
"POST" = a type of HTTP request used to SEND data to the server.

We run this with: uvicorn main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agents import run_research_pipeline

# ──────────────────────────────────────────────
# Create the FastAPI app
# This is the main application object
# Everything we build attaches to this
# ──────────────────────────────────────────────
app = FastAPI(
    title="Multi-Agent Research Assistant",
    description="A research assistant powered by 3 AI agents that search, summarize, and write reports.",
    version="1.0.0"
)

# ──────────────────────────────────────────────
# CORS Middleware
# ──────────────────────────────────────────────
# CORS = Cross-Origin Resource Sharing
# In simple words: By default, a web page can only talk to
# its own server. Our Streamlit app runs on port 8501
# but FastAPI runs on port 8000. Without CORS, the browser
# would BLOCK Streamlit from talking to FastAPI.
# This middleware says "hey, it's okay, let anyone connect."
# ──────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # Allow any website to connect
    allow_credentials=True,
    allow_methods=["*"],       # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],       # Allow all headers
)


# ──────────────────────────────────────────────
# Request Model
# ──────────────────────────────────────────────
# This defines what data the API EXPECTS to receive.
# When someone sends a POST request to /research,
# they MUST send a JSON body like: {"topic": "quantum computing"}
#
# BaseModel is from Pydantic — it automatically validates
# the data (checks that "topic" is a string, etc.)
# If someone sends bad data, FastAPI returns an error automatically.
# ──────────────────────────────────────────────
class ResearchRequest(BaseModel):
    topic: str   # The research topic, e.g., "quantum computing"


# ──────────────────────────────────────────────
# Response Model
# ──────────────────────────────────────────────
# This defines what data the API SENDS BACK.
# It tells FastAPI (and anyone reading the docs)
# exactly what shape the response will be.
# ──────────────────────────────────────────────
class ResearchResponse(BaseModel):
    topic: str            # The original topic
    search_results: str   # Raw search results from Agent 1
    summary: str          # Bullet point summary from Agent 2
    report: str           # Final formatted report from Agent 3


# ──────────────────────────────────────────────
# THE ONE AND ONLY ENDPOINT: POST /research
# ──────────────────────────────────────────────
# This is where the magic happens!
# When someone sends a POST request to /research with a topic,
# this function runs the entire 3-agent pipeline and returns the results.
#
# @app.post = "when someone sends a POST request to this URL, run this function"
# response_model = tells FastAPI what the response looks like (for auto-docs)
# ──────────────────────────────────────────────
@app.post("/research", response_model=ResearchResponse)
def do_research(request: ResearchRequest):
    """
    Takes a research topic and runs it through the 3-agent pipeline:
    1. Researcher Agent searches the internet
    2. Summarizer Agent creates bullet points
    3. Report Writer Agent creates a final report
    """
    # Run the pipeline from agents.py
    # This calls all 3 agents one after another
    result = run_research_pipeline(request.topic)

    # Return the result — FastAPI automatically converts it to JSON
    return result


# ──────────────────────────────────────────────
# Health Check Endpoint
# ──────────────────────────────────────────────
# A simple GET endpoint to check if the server is running.
# You can visit http://localhost:8000/health in your browser.
# If it returns {"status": "healthy"}, the server is working!
# ──────────────────────────────────────────────
@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Multi-Agent Research Assistant is running!"}
