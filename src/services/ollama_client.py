import json
import subprocess
import logging
from typing import Dict, Any
from fastapi import HTTPException

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
        # 1. Выбираем системный и пользовательский шаблоны
        system_prompt = self.SUMMARY_SYSTEM_PROMPT if is_summary else self.QA_SYSTEM_PROMPT
        user_prompt = (self.SUMMARY_USER_PROMPT if is_summary else self.QA_USER_PROMPT).format(
            transcript=transcript
        )

        # 2. Собираем единый текст запроса
        full_prompt = f"{system_prompt}\n\n{user_prompt}"

        # 3. Формируем команду с позиционным PROMPT и флагом --format json
        cmd = [
            "ollama", "run", MODEL,
            full_prompt,
            "--format", "json"
        ]

        try:
            logger.debug(f"Running Ollama CLI: {' '.join(cmd[:3])} <PROMPT> {' '.join(cmd[4:])}")
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False
            )

            if res.returncode != 0:
                err = res.stderr.strip() or res.stdout.strip() or "Unknown error"
                logger.error(f"Ollama CLI failed ({res.returncode}): {err}")
                raise HTTPException(500, detail=f"Ollama error: {err}")

            # 4. Парсим JSON-ответ
            data = json.loads(res.stdout)
            # Обычно в поле "response"
            if "response" in data:
                return data["response"].strip()
            # или, на всякий случай, в choices
            if "choices" in data and data["choices"]:
                return data["choices"][0]["message"]["content"].strip()

            raise HTTPException(500, detail="Unexpected Ollama output format")

        except (subprocess.SubprocessError, json.JSONDecodeError) as e:
            logger.error(f"Error during Ollama generation: {e}", exc_info=True)
            raise HTTPException(500, detail=f"Generation error: {e}")
