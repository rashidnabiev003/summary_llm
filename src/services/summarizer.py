import logging
from typing import Dict, Any
from fastapi import HTTPException

from .ollama_client import OllamaClient

logger = logging.getLogger(__name__)

class SummarizerService:
    def __init__(self):
        """
        Initialize summarizer service.
        """
        self.ollama = OllamaClient()
        
    async def generate_summary(self, transcript: str) -> str:
        """
        Summarize meeting transcript.
        
        Args:
            transcript: The meeting transcript to summarize
            
        Returns:
            str: Generated summary text
            
        Raises:
            HTTPException: If there's an error during summarization
        """
        try:
            # Generate summary
            result = self.ollama.generate_summary(transcript)
            
            logger.info(f"Successfully generated summary for transcript of length {len(transcript)}")
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error during summarization: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error during summarization: {str(e)}"
            )
            
    async def generate_qa(self, transcript: str) -> str:
        """
        Generate QA for meeting transcript.
        
        Args:
            transcript: The meeting transcript to analyze
            
        Returns:
            str: Generated QA text
            
        Raises:
            HTTPException: If there's an error during QA generation
        """
        try:
            # Generate QA
            result = self.ollama.generate_qa(transcript)
            
            logger.info(f"Successfully generated QA for transcript of length {len(transcript)}")
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error during QA generation: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error during QA generation: {str(e)}"
            ) 