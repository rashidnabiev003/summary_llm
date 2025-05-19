from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Literal
import requests
import json

# Ollama API configuration
OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen"

# Prompts for different modes
SUMMARY_PROMPT = """Объемно суммаризируй текст совещания строго в формате:
# Дата: [дата]
# Решения:
- [пункт] (Ответственный: @имя)
# Вопросы:

Текст совещания:
{transcript}"""

QA_PROMPT = """Выдели цепочки Вопрос-Ответ из стенограммы совещания, пропускай бессмысленные вопросы. Формат:
- Вопрос: ...
  Ответ: ...

Текст совещания:
{transcript}"""

# Input data structure
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

app = FastAPI()

def generate_with_ollama(prompt: str) -> str:
    """Generate text using Ollama API"""
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "top_p": 0.95,
            "max_tokens": 4096
        }
    }
    
    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        return response.json()["response"].strip()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error calling Ollama API: {str(e)}")

@app.post("/analyze_meeting")
async def analyze_meeting(
    req: MeetingRequest,
    mode: Literal["summary", "qa"] = Query(
        "summary",
        description="Режим работы: 'summary' для итоговой сводки, 'qa' для цепочек Вопрос-Ответ"
    )
):
    entries = req.entries
    if not entries:
        raise HTTPException(status_code=400, detail="No timeline entries provided")

    # Sort entries by time.begin to ensure chronological order
    sorted_entries = sorted(entries, key=lambda x: float(x.time.begin))
    
    transcript = "\n".join(
        f"[{entry.time.begin}-{entry.time.end}] {entry.name}: {entry.text}" 
        for entry in sorted_entries
    )

    # Select prompt based on mode
    if mode == "summary":
        prompt = SUMMARY_PROMPT.format(transcript=transcript)
    else:  # mode == 'qa'
        prompt = QA_PROMPT.format(transcript=transcript)

    result = generate_with_ollama(prompt)
    return {"result": result}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 