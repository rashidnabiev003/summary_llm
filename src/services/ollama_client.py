import json
import subprocess
import logging
from typing import Dict, Any, List
from fastapi import HTTPException
import ollama

logger = logging.getLogger(__name__)
MODEL = "qwen3:14b"

class OllamaClient:
    SUMMARY_SYSTEM_PROMPT = (
        "You are an AI assistant that summarizes meeting transcripts "
        "accurately and concisely. Your summaries are well-structured and highlight the key points."
    )
    QA_SYSTEM_PROMPT = (
        "You are an AI assistant that analyzes meeting transcripts and extracts important information. "
        "Focus on providing clear answers to the questions about topics, decisions, action items, "
        "responsibilities, and deadlines."
    )

    SUMMARY_USER_PROMPT = """Summarize the following meeting transcript in 3-5 paragraphs. \
Focus on key points, decisions made, and action items. Be concise but comprehensive.

Transcript:
{transcript}"""
    QA_USER_PROMPT = """Based on the following meeting transcript, answer these questions:
1. What are the main topics discussed?
2. What decisions were made?
3. What are the next steps or action items?
4. Who has responsibility for different tasks?
5. What deadlines or timeframes were mentioned?

Transcript:
{transcript}"""
    def __init__(self):
        """
        Initialize Ollama client.
        """
        self.model = MODEL
  
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
        system_prompt = self.SUMMARY_SYSTEM_PROMPT if is_summary else self.QA_SYSTEM_PROMPT
        user_prompt = (
            self.SUMMARY_USER_PROMPT if is_summary else self.QA_USER_PROMPT
        ).format(transcript=transcript)

        messages: List[Dict[str, str]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ]

        try:
            logger.debug(f"Calling ollama.chat(model={self.model}, messages=[...])")
            response = ollama.chat(model=self.model, messages=messages)
            # response format: {"message": {"role": ..., "content": ...}}
            if not response or "message" not in response or "content" not in response["message"]:
                raise HTTPException(status_code=500, detail="Invalid response structure from Ollama")

            content = response["message"]["content"].strip()
            logger.debug("Received content from Ollama")
            return content

        except Exception as e:
            logger.error(f"Error during Ollama generation: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Generation error: {str(e)}")
