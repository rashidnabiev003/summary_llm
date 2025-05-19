from pydantic import BaseModel
from typing import List

class TimeRange(BaseModel):
    begin: str
    end: str

class TimelineEntry(BaseModel):
    id: int
    time: TimeRange
    name: str
    text: str

class MeetingRequest(BaseModel):
    entries: List[TimelineEntry] 