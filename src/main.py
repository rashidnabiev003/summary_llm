import logging
import json
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from fastapi.middleware.cors import CORSMiddleware

from src.schemas import MeetingRequest, MeetingEntry, MeetingEntryList
from src.services.summarizer import SummarizerService

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

async def process_entries(entries: List[MeetingEntry]) -> str:
    """Объединить записи в один транскрипт"""
    combined_text = "\n\n".join([
        f"[{entry.time.begin} - {entry.time.end}] {entry.name}: {entry.text}"
        for entry in entries
    ])
    return combined_text

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/summarize")
async def summarize_meeting(request: MeetingRequest) -> Dict[str, Any]:
    """
    Summarize meeting transcript
    
    Args:
        request: Meeting request with entries
    
    Returns:
        Dict with think and result fields
    """
    try:
        # Используем entries из запроса
        combined_text = await process_entries(request.entries)
        
        # Generate summary
        response = await summarizer.generate_summary(combined_text)
        
        logger.info(f"Successfully summarized meeting with {len(request.entries)} entries")
        return response
        
    except Exception as e:
        logger.error(f"Error summarizing meeting: {str(e)}")
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(
            status_code=500,
            detail=f"Error summarizing meeting: {str(e)}"
        )

@app.post("/summarize/list")
async def summarize_meeting_list(entries: MeetingEntryList) -> Dict[str, Any]:
    """
    Summarize meeting transcript from direct list of entries
    
    Args:
        entries: List of meeting entries
    
    Returns:
        Dict with think and result fields
    """
    try:
        # Объединяем записи напрямую
        combined_text = await process_entries(entries)
        
        # Generate summary
        response = await summarizer.generate_summary(combined_text)
        
        logger.info(f"Successfully summarized meeting with {len(entries)} entries")
        return response
        
    except Exception as e:
        logger.error(f"Error summarizing meeting: {str(e)}")
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(
            status_code=500,
            detail=f"Error summarizing meeting: {str(e)}"
        )

@app.post("/summarize/file")
async def summarize_meeting_file(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Summarize meeting transcript from uploaded JSON file
    
    Args:
        file: JSON file with meeting entries list
    
    Returns:
        Dict with think and result fields
    """
    try:
        # Читаем файл
        contents = await file.read()
        entries_data = json.loads(contents)
        
        # Валидируем и преобразуем данные в модель
        entries = [MeetingEntry(**entry) for entry in entries_data]
        
        # Объединяем записи
        combined_text = await process_entries(entries)
        
        # Generate summary
        response = await summarizer.generate_summary(combined_text)
        
        logger.info(f"Successfully summarized meeting from file with {len(entries)} entries")
        return response
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file")
    except Exception as e:
        logger.error(f"Error summarizing meeting from file: {str(e)}")
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(
            status_code=500,
            detail=f"Error summarizing meeting from file: {str(e)}"
        )

@app.post("/qa")
async def meeting_qa(request: MeetingRequest) -> Dict[str, Any]:
    """
    Generate QA for meeting transcript
    
    Args:
        request: Meeting request with entries
    
    Returns:
        Dict with think and result fields
    """
    try:
        # Используем entries из запроса
        combined_text = await process_entries(request.entries)
        
        # Generate QA
        response = await summarizer.generate_qa(combined_text)
        
        logger.info(f"Successfully generated QA for meeting with {len(request.entries)} entries")
        return response
        
    except Exception as e:
        logger.error(f"Error generating QA for meeting: {str(e)}")
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(
            status_code=500,
            detail=f"Error generating QA for meeting: {str(e)}"
        )

@app.post("/qa/list")
async def meeting_qa_list(entries: MeetingEntryList) -> Dict[str, Any]:
    """
    Generate QA for meeting transcript from direct list of entries
    
    Args:
        entries: List of meeting entries
    
    Returns:
        Dict with think and result fields
    """
    try:
        # Объединяем записи напрямую
        combined_text = await process_entries(entries)
        
        # Generate QA
        response = await summarizer.generate_qa(combined_text)
        
        logger.info(f"Successfully generated QA for meeting with {len(entries)} entries")
        return response
        
    except Exception as e:
        logger.error(f"Error generating QA for meeting: {str(e)}")
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(
            status_code=500,
            detail=f"Error generating QA for meeting: {str(e)}"
        )

@app.post("/qa/file")
async def meeting_qa_file(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Generate QA for meeting transcript from uploaded JSON file
    
    Args:
        file: JSON file with meeting entries list
    
    Returns:
        Dict with think and result fields
    """
    try:
        # Читаем файл
        contents = await file.read()
        entries_data = json.loads(contents)
        
        # Валидируем и преобразуем данные в модель
        entries = [MeetingEntry(**entry) for entry in entries_data]
        
        # Объединяем записи
        combined_text = await process_entries(entries)
        
        # Generate QA
        response = await summarizer.generate_qa(combined_text)
        
        logger.info(f"Successfully generated QA from file with {len(entries)} entries")
        return response
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file")
    except Exception as e:
        logger.error(f"Error generating QA from file: {str(e)}")
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(
            status_code=500,
            detail=f"Error generating QA from file: {str(e)}"
        ) 