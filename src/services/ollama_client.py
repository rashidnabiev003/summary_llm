import json
import subprocess
import logging
from typing import Dict, Any, List
from fastapi import HTTPException
from src.schemas import AppConfig
import ollama


def load_config(path: str = "config.json") -> AppConfig:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return AppConfig(**data)

cfg = load_config()

logger = logging.getLogger(__name__)
MODEL = cfg.ollama.MODEL_NAME

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

    SUMMARY_USER_PROMPT = """Изложите следующую запись совещания. 
Сосредоточьтесь на ключевых моментах, принятых решениях и действиях. Будьте краткими, но всесторонними.

Ваш ответ ДОЛЖЕН соответствовать следующему формату:
<think>
Здесь вы анализируете содержание, определяете ключевые моменты и важные детали.
</think>
А затем собственно резюме.

Расшифровка:
{transcript}"""

    QA_USER_PROMPT = """Основываясь на следующей стенограмме совещания, ответьте на следующие вопросы: 
1. Какие основные темы обсуждались? 
2. Какие решения были приняты? 
3. Каковы следующие шаги или действия? 
4. Кто отвечает за выполнение различных задач? 
5. Какие сроки или временные рамки были упомянуты? 

Формат ответов для каждой темы должен быть такой:
Тема: <название темы>
Исполнитель: <Имя исполнителя>
Сроки: <Сроки выполнения>
Примечания: <примечания> (добавить опционально)

Ваш вывода должен соответствовать следующему формату: 
<think>
Здесь вы анализируете содержание, определяете необходимую информацию для ответа на каждый вопрос.
</think>
А теперь настоящие ответы на каждый вопрос.

Расшифровка:
{transcript}"""

    def __init__(self):
        """
        Initialize Ollama client.
        """
        self.model = MODEL
  
    def generate_summary(self, transcript: str) -> Dict[str, str]:
        """
        Generate summary using Ollama CLI
        
        Args:
            transcript: The meeting transcript to summarize
            
        Returns:
            Dict containing "think" and "result" parts
            
        Raises:
            HTTPException: If there's an error during generation
        """
        return self._generate(transcript, is_summary=True)
        
    def generate_qa(self, transcript: str) -> Dict[str, str]:
        """
        Generate QA using Ollama CLI
        
        Args:
            transcript: The meeting transcript to analyze
            
        Returns:
            Dict containing "think" and "result" parts
            
        Raises:
            HTTPException: If there's an error during generation
        """
        return self._generate(transcript, is_summary=False)
        
    def _generate(self, transcript: str, is_summary: bool) -> Dict[str, str]:
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
            
            # Разделяем ответ на <think> и result
            think_part = ""
            result_part = content
            
            if "<think>" in content and "</think>" in content:
                think_part = content.split("<think>")[1].split("</think>")[0].strip()
                result_part = content.split("</think>")[1].strip()
            
            return {
                "think": think_part,
                "result": result_part
            }

        except Exception as e:
            logger.error(f"Error during Ollama generation: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Generation error: {str(e)}")
