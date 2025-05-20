import logging
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .schemas import MeetingRequest
from .services.summarizer import SummarizerService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Meeting Summarizer API",
    description="API for summarizing meeting transcripts using Ollama and Qwen model",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
summarizer = SummarizerService()

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/summarize")
async def summarize_meeting(request: MeetingRequest) -> Dict[str, str]:
    """
    Summarize meeting transcript
    
    Args:
        request: Meeting request with entries
    
    Returns:
        Dict with result field containing the summary
    """
    try:
        # Combine all meeting entries into a single transcript
        combined_text = "\n\n".join([
            f"[{entry.time.begin} - {entry.time.end}] {entry.name}: {entry.text}"
            for entry in request.entries
        ])
        
        # Generate summary
        result_text = await summarizer.generate_summary(combined_text)
        
        logger.info(f"Successfully summarized meeting with {len(request.entries)} entries")
        return {"result": result_text}
        
    except Exception as e:
        logger.error(f"Error summarizing meeting: {str(e)}")
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(
            status_code=500,
            detail=f"Error summarizing meeting: {str(e)}"
        )

@app.post("/qa")
async def meeting_qa(request: MeetingRequest) -> Dict[str, str]:
    """
    Generate QA for meeting transcript
    
    Args:
        request: Meeting request with entries
    
    Returns:
        Dict with result field containing the QA
    """
    try:
        # Combine all meeting entries into a single transcript
        combined_text = "\n\n".join([
            f"[{entry.time.begin} - {entry.time.end}] {entry.name}: {entry.text}"
            for entry in request.entries
        ])
        
        # Generate QA
        result_text = await summarizer.generate_qa(combined_text)
        
        logger.info(f"Successfully generated QA for meeting with {len(request.entries)} entries")
        return {"result": result_text}
        
    except Exception as e:
        logger.error(f"Error generating QA for meeting: {str(e)}")
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(
            status_code=500,
            detail=f"Error generating QA for meeting: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=49137,
        log_level="info",
    ) 