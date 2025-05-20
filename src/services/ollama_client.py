import json
import subprocess
import logging
from typing import Dict, Any
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class OllamaClient:
    # Встроенные промпты для пользователя
    SUMMARY_PROMPT = """Summarize the following meeting transcript in 3-5 paragraphs. Focus on key points, decisions made, and action items. Be concise but comprehensive.

Transcript:
{transcript}"""

    QA_PROMPT = """Based on the following meeting transcript, answer these questions:
1. What are the main topics discussed?
2. What decisions were made?
3. What are the next steps or action items?
4. Who has responsibility for different tasks?
5. What deadlines or timeframes were mentioned?

Transcript:
{transcript}"""

    # Системные промпты для модели
    SUMMARY_SYSTEM_PROMPT = "You are an AI assistant that summarizes meeting transcripts accurately and concisely. Your summaries are well-structured and highlight the key points."

    QA_SYSTEM_PROMPT = "You are an AI assistant that analyzes meeting transcripts and extracts important information. Focus on providing clear answers to the questions about topics, decisions, action items, responsibilities, and deadlines."

    def __init__(self):
        """
        Initialize Ollama client.
        """
        pass
  
    def generate_summary(self, transcript: str) -> str:
        """
        Generate summary using Ollama CLI
        
        Args:
            transcript: The meeting transcript to summarize
            
        Returns:
            str: Generated summary
            
        Raises:
            HTTPException: If there's an error during generation
        """
        return self._generate(transcript, is_summary=True)
        
    def generate_qa(self, transcript: str) -> str:
        """
        Generate QA using Ollama CLI
        
        Args:
            transcript: The meeting transcript to analyze
            
        Returns:
            str: Generated QA
            
        Raises:
            HTTPException: If there's an error during generation
        """
        return self._generate(transcript, is_summary=False)
        
    def _generate(self, transcript: str, is_summary: bool) -> str:
        """
        Generate text using Ollama CLI
        
        Args:
            transcript: The meeting transcript to process
            is_summary: If True, use summary mode, otherwise use QA mode
            
        Returns:
            str: Generated text response
            
        Raises:
            HTTPException: If there's an error during generation
        """
        # Выбор соответствующего промпта и системного промпта
        if is_summary:
            prompt = self.SUMMARY_PROMPT
            system_prompt = self.SUMMARY_SYSTEM_PROMPT
        else:
            prompt = self.QA_PROMPT
            system_prompt = self.QA_SYSTEM_PROMPT
            
        formatted_prompt = prompt.format(transcript=transcript)
        
        # Добавляем системный промпт в команду
        cmd = [
            "ollama", "run", "qwen",
            "--prompt", formatted_prompt,
            "--system", system_prompt,
            "--max-tokens", "500",
            "--temperature", "0.2",
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
