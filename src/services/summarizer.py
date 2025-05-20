import logging
from typing import Dict, Any
from fastapi import HTTPException

from .ollama_client import OllamaClient
from ..config import Config

logger = logging.getLogger(__name__)

class SummarizerService:
    def __init__(self, config: Config = None):
        """
        Initialize summarizer service.
        
        Args:
            config: Optional Config instance. If not provided, creates a new one.
        """
        self.config = config or Config()
        self.ollama = OllamaClient(self.config)
        
    async def summarize(self, transcript: str, mode: str = "summary") -> Dict[str, Any]:
        """
        Summarize meeting transcript.
        
        Args:
            transcript: The meeting transcript to summarize
            mode: The mode to use ('summary' or 'qa')
            
        Returns:
            Dict containing the summary and metadata
            
        Raises:
            HTTPException: If there's an error during summarization
        """
        try:
            # Get formatted prompt
            prompt = self.ollama.get_prompt(mode, transcript)
            
            # Generate summary
            summary = self.ollama.generate(prompt)
            
            # Prepare response
            response = {
                "summary": summary,
                "metadata": {
                    "mode": mode,
                    "model": "qwen",
                    "transcript_length": len(transcript)
                }
            }
            
            logger.info(f"Successfully generated {mode} for transcript of length {len(transcript)}")
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error during summarization: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error during summarization: {str(e)}"
            ) 