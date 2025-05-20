from pydantic import BaseModel
from typing import List, Optional

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
    """Модель для запроса на анализ совещания"""
    entries: List[MeetingEntry] 