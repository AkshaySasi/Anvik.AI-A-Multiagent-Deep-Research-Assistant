from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.backend.agents import Orchestrator
from src.backend.models.research_models import ResearchReport
from pydantic import BaseModel
from src.backend.utils.logger import setup_logger
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = FastAPI(title="Anvik.ai API")
logger = setup_logger("anvik_ai")

# Configure CORS for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:7860", "https://anvik-ai.onrender.com"],  # Update with your Render URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = Orchestrator()

class ResearchRequest(BaseModel):
    topic: str

@app.post("/research", response_model=ResearchReport)
async def research_topic(request: ResearchRequest):
    try:
        logger.info(f"Received research request for topic: {request.topic}")
        report = await orchestrator.research_topic(request.topic)
        return report
    except Exception as e:
        logger.error(f"Error processing research request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/progress/{topic}")
async def track_progress(topic: str):
    try:
        result = await orchestrator.track_research_progress(topic)
        return {"message": result}
    except Exception as e:
        logger.error(f"Error tracking progress: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/proposal/{topic}")
async def generate_proposal(topic: str):
    try:
        result = await orchestrator.generate_research_proposal(topic)
        return {"proposal": result}
    except Exception as e:
        logger.error(f"Error generating proposal: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))