import json
from fastapi import FastAPI, HTTPException, Query
from typing import Literal

from src.utils.schemas import MeetingRequest
from ollama_client.ollama_client import OllamaClient

# Load server configuration
with open("config.json", 'r') as f:
    config = json.load(f)

app = FastAPI()
ollama_client = OllamaClient()

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

    prompt = ollama_client.get_prompt(mode, transcript)
    result = ollama_client.generate(prompt)
    return {"result": result}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=config['server']['host'], 
        port=config['server']['port']
    ) 