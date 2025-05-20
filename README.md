# Meeting Summarizer API

A microservice for summarizing meeting transcripts using Ollama and the Qwen model.

## Features

- Summarize meeting transcripts
- Generate Q&A from meeting transcripts
- Uses Ollama with Qwen model
- Built-in prompt templates and system prompts

## Prerequisites

- Python 3.8+
- [Ollama](https://ollama.ai/) installed
- Qwen model pulled in Ollama (`ollama pull qwen`)

## Project Structure

```
├── src/
│   ├── services/
│   │   ├── __init__.py     # Services package
│   │   ├── ollama_client.py # Ollama API client
│   │   └── summarizer.py   # Summarizer service
│   ├── main.py             # FastAPI application
│   └── schemas.py          # Pydantic models
└── requirements.txt        # Dependencies
```

## Installation

1. Clone the repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Make sure Ollama is installed and running:

```bash
ollama pull qwen
```

## Running the Service

Start the server:

```bash
python -m src.main
```

The API will be available at http://localhost:8000

## API Endpoints

- `GET /health` - Health check endpoint
- `POST /summarize` - Summarize meeting transcript
- `POST /qa` - Generate Q&A from meeting transcript

## Example Request

```bash
curl -X POST http://localhost:8000/summarize \
  -H "Content-Type: application/json" \
  -d '{
    "entries": [
      {
        "id": 1,
        "time": {
          "begin": "00:00:00",
          "end": "00:00:30"
        },
        "name": "John",
        "text": "Welcome everyone to our weekly meeting."
      },
      {
        "id": 2,
        "time": {
          "begin": "00:00:31",
          "end": "00:01:00"
        },
        "name": "Alice",
        "text": "Today we need to discuss the project timeline."
      }
    ]
  }'
```

## Customization

The service can be customized by editing the prompts directly in the `src/services/ollama_client.py` file:

- User prompts:
  - `SUMMARY_PROMPT` - The prompt template for summarization
  - `QA_PROMPT` - The prompt template for Q&A generation
  
- System prompts:
  - `SUMMARY_SYSTEM_PROMPT` - The system prompt for summary mode
  - `QA_SYSTEM_PROMPT` - The system prompt for QA mode