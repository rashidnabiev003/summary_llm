from pydantic import BaseModel, Field
from typing import List, Optional, Union
from fastapi import UploadFile, File

class TimeRange(BaseModel):
    """Модель для временного диапазона записи"""
    begin: str
    end: str

class MeetingEntry(BaseModel):
    """Модель для записи совещания"""
    id: int
    time: TimeRange
    name: str
    text: str

class MeetingRequest(BaseModel):
    """Модель для запроса на анализ совещания (для обратной совместимости)"""
    entries: List[MeetingEntry]
    
    class Config:
        schema_extra = {
            "example": {
                "entries": [
                    {
                        "id": 1,
                        "time": {"begin": "00:00:00", "end": "00:00:30"},
                        "name": "Юрий_Силаев",
                        "text": "Видимо, можно начинать. Во-первых, наверное, надо сказать спасибо..."
                    }
                ]
            }
        }
        
# Для прямого приема списка записей
MeetingEntryList = List[MeetingEntry] 

class OllamaConfig(BaseModel):
    MODEL_NAME: str
    ollama_version: str
    ollama_url: str

class ServerConfig(BaseModel):
    port: str
    host: str

class AppConfig(BaseModel):
    """Модель для конфигураций системы"""
    ollama: OllamaConfig
    server: ServerConfig

class Info(BaseModel):
    name: str
    version: str
    model_status: str
    server: str