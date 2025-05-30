# Meeting Summarizer API

A microservice for summarizing meeting transcripts using Ollama and the Qwen model.

## Features

- Summarize meeting transcripts
- Generate Q&A from meeting transcripts
- Enhanced response format with "think" and "result" sections
- Support for direct lists of meeting entries (without "entries" wrapper)
- File upload support for JSON data
- Uses Ollama with Qwen model
- Built-in prompt templates and system prompts
- Optimized architecture with embedded prompts

## Prerequisites

- Python 3.12
- [Ollama](https://ollama.ai/) installed
- Qwen model pulled in Ollama (`ollama pull qwen3:14b`)

## Project Structure

```
├── src/
│   ├── services/
│   │   ├── __init__.py     # Services package
│   │   ├── ollama_client.py # Ollama API client
│   │   └── summarizer.py   # Summarizer service
│   ├── main.py             # FastAPI application
│   ├── schemas.py          # Pydantic models
├── run.py                  # Script for launching the application
├── requirements.txt        # Dependencies
├── setup.py                # Script for correctly import libraries
└── .gitingnore
```

## Installation

1. Clone the repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Make sure Ollama is installed and running:

```bash
ollama pull qwen3:14b
```


## API Endpoints

- `GET /health` - Health check endpoint
- `POST /summarize/list` - Summarize meeting transcript (direct list format)
- `POST /summarize/file` - Summarize meeting transcript from uploaded JSON file
- `POST /qa/list` - Generate Q&A from meeting transcript (direct list format)
- `POST /qa/file` - Generate Q&A from meeting transcript from uploaded JSON file

## Response Format

All response endpoints return a structured format with two sections:

```json
{
  "think": "The model's analytical thoughts and reasoning process",
  "result": "The final summarized output or Q&A"
}
```

## Example Request

```bash
curl -X POST http://localhost:49137/summarize/list \
  -H "Content-Type: application/json" \
  -d '[
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
  ]'
```

### File Upload

```bash
curl -X POST http://localhost:49137/summarize/file \
  -F "file=@meeting_data.json"
```

## Customization

The service can be customized by editing the prompts directly in the `src/services/ollama_client.py` file:

- User prompts:
  - `SUMMARY_USER_PROMPT` - The prompt template for summarization
  - `QA_USER_PROMPT` - The prompt template for Q&A generation
  
- System prompts:
  - `SUMMARY_SYSTEM_PROMPT` - The system prompt for summary mode
  - `QA_SYSTEM_PROMPT` - The system prompt for QA mode