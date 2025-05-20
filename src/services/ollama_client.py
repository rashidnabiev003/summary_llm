import json
import subprocess
import logging
from typing import Dict, Any
from fastapi import HTTPException

from ..config import Config

logger = logging.getLogger(__name__)

system_prompt_qa = """ qa prompt"""

system_prompt_summary = """ summary prompt"""


class OllamaClient:
    def __init__(self, config: Config = None):
        """
        Initialize Ollama client.
        
        Args:
            config: Optional Config instance. If not provided, creates a new one.
        """
        self.config = config or Config()
        self.prompts = self.config.prompts_config
  
    def generate(self, prompt: str) -> str:
        """
        Generate text using Ollama CLI
        
        Args:
            prompt: The prompt to send to the model
            
        Returns:
            str: Generated text response
            
        Raises:
            HTTPException: If there's an error during generation
        """
        cmd = [
            "ollama", "run", "qwen3:14b",
            "--prompt", prompt,
            "--system",
            "--json"
        ]
        
        try:
            logger.debug(f"Executing Ollama command: {' '.join(cmd)}")
            res = subprocess.run(cmd, capture_output=True, text=True)
            
            if res.returncode != 0:
                error_msg = res.stderr.strip() or "Unknown error"
                logger.error(f"Ollama command failed: {error_msg}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Ollama command failed: {error_msg}"
                )
                
            response = json.loads(res.stdout)["response"].strip()
            logger.debug("Successfully generated response from Ollama")
            return response
            
        except subprocess.SubprocessError as e:
            logger.error(f"Error executing Ollama command: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error executing Ollama command: {str(e)}"
            )
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing Ollama response: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error parsing Ollama response: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error during generation: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error: {str(e)}"
            )

    def get_prompt(self, mode: str, transcript: str) -> str:
        """
        Get formatted prompt based on mode
        
        Args:
            mode: The mode to use ('summary' or 'qa')
            transcript: The meeting transcript to summarize
            
        Returns:
            str: Formatted prompt
            
        Raises:
            HTTPException: If mode is invalid
        """
        if mode not in self.prompts:
            logger.error(f"Invalid mode requested: {mode}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid mode: {mode}. Supported modes: {list(self.prompts.keys())}"
            )
            
        try:
            return self.prompts[mode].format(transcript=transcript)
        except Exception as e:
            logger.error(f"Error formatting prompt: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error formatting prompt: {str(e)}"
            )
