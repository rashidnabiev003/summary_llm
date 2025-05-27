import logging
import json
import requests
import datetime
import ollama
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.schemas import MeetingRequest, MeetingEntry, MeetingEntryList, AppConfig, Info
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
    version="1.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_config(path: str = "config.json") -> AppConfig:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return AppConfig(**data)

cfg = load_config()

def get_utc_timestamp():
    return datetime.datetime.utcnow().isoformat() + "Z"

# Initialize services
summarizer = SummarizerService()

async def process_entries(entries: List[MeetingEntry]) -> str:
    """Объединить записи в один транскрипт"""
    combined_text = "\n\n".join([
        f"[{entry.time.begin} - {entry.time.end}] {entry.name}: {entry.text}"
        for entry in entries
    ])
    return combined_text

@app.get("/ping")
async def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    try:
        res = requests.get(f"{cfg.ollama.ollama_url}/api/tags", timeout=5)
        res.raise_for_status()
        
        models = ollama.list()
        names = [m["name"] for m in models.get("models", [])]
        
        if cfg.ollama.MODEL_NAME not in names:
            return {
                "status": "unavailable",
                "error": f"{cfg.ollama.MODEL_NAME} is not found",
                "timestamp": get_utc_timestamp()
            }

        return {
            "status": "pong",
            "timestamp": get_utc_timestamp()
        }


    except requests.exceptions.ConnectionError:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unavailable",
                "error": "server not running",
                "timestamp": get_utc_timestamp()
            }
        )
    except requests.exceptions.Timeout:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unavailable",
                "error": "timeout",
                "timestamp": get_utc_timestamp()
            }
        )
    except requests.exceptions.RequestException as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unavailable",
                "error": str(e),
                "timestamp": get_utc_timestamp()
            }
        )
    except Exception as e:
        logger.error(f"Error when checking model status: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error": str(e),
                "timestamp": get_utc_timestamp()
            }
        )
        
@app.get("/info", response_model=Info)
async def info() -> Info:
    model_status = "Enabled"
    server_status = "Connected"
    try:
        res = requests.get(f"{cfg.ollama.ollama_url}/api/tags", timeout=5)
        res.raise_for_status()
        
        models = ollama.list()
        names = [m["name"] for m in models.get("models", [])]
        
        if cfg.ollama.MODEL_NAME not in names:
            model_status = "Model not found"

    except requests.exceptions.ConnectionError:
        server_status = "Connection error"

    except requests.exceptions.Timeout:
        server_status = "Connection error"
    
    return Info(
        name="Meeting Summarizer API",
        version="1.1.0",
        model_status=model_status,
        server=server_status
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
            detail=f"Error summarizing meeting: {str(e)}",
            content={
                "error": "generation errror",
                "message": f"Error summarizing meeting:  {str(e)}",
                "timestamp": get_utc_timestamp()
            }
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
            status_code=501,
            detail=f"Error summarizing meeting from file: {str(e)}",
            content={
                "error": "generation errror",
                "message": f"Error summarizing meeting from file:  {str(e)}",
                "timestamp": get_utc_timestamp()
            }
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
            detail=f"Error generating QA for meeting: {str(e)}",
            content={
                "error": "generation errror",
                "message": f"Error generating QA: {str(e)}",
                "timestamp": get_utc_timestamp()
            }
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
            status_code=501,
            detail=f"Error generating QA from file: {str(e)}",
            content={
                "error": "generation errror",
                "message": f"Error generating QA from file: {str(e)}",
                "timestamp": get_utc_timestamp()
            }
        ) 