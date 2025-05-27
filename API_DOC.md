# API Documentation for Meeting Summarizer

## Overview

The API version is "1.1.0".

## Configuration

The API uses a `config.json` file to configure:

* **Ollama Model**: `MODEL_NAME` (e.g., "qwen3:14b")
* **Ollama URL**: `ollama_url` (e.g., "<http://localhost:11434>")
* **Server**: `host` and `port` for the API itself.

## Endpoints

* `GET /ping` - Health check endpoint
* `GET /info` - Get information about api and status
* `POST /summarize/list` - Summarize meeting transcript (direct list format)
* `POST /summarize/file` - Summarize meeting transcript from uploaded JSON file
* `POST /qa/list` - Generate Q&A from meeting transcript (direct list format)
* `POST /qa/file` - Generate Q&A from meeting transcript from uploaded JSON file

### Health Check

#### `GET /ping`

Checks the health of the API and its connection to the Ollama service.

**Responses:**

* **200 OK (Success)**

  ```json
  {
    "status": "pong",
    "timestamp": "YYYY-MM-DDTHH:MM:SS.ffffffZ"
  }
  ```
* **200 OK (Model Unavailable)**: Ollama server is running, but the configured model is not found.

  ```json
  {
    "status": "unavailable",
    "error": "<MODEL_NAME> is not found",
    "timestamp": "YYYY-MM-DDTHH:MM:SS.ffffffZ"
  }
  ```
* **503 Service Unavailable**: Ollama server not running or connection timeout.

  ```json
  {
    "status": "unavailable",
    "error": "server not running" / "timeout" / "<specific connection error>",
    "timestamp": "YYYY-MM-DDTHH:MM:SS.ffffffZ"
  }
  ```
* **500 Internal Server Error**: Other unexpected errors.

  ```json
  {
    "status": "error",
    "error": "<error message string>",
    "timestamp": "YYYY-MM-DDTHH:MM:SS.ffffffZ"
  }
  ```

### API Information

#### `GET /info`

Provides information about the API.

**Response (200 OK):**

```json
{
  "name": "Meeting Summarizer API",
  "version": "1.1.0",
  "model_status": "Enabled" / "Model not found",
  "server": "Connected" / "Connection error"
}
```

### Summarization

#### `POST /summarize/list`

Summarizes a meeting transcript provided as a JSON list of entries in the request body.

**Request Body (**`**application/json**`**):** A list of `MeetingEntry` objects:

```json
[
  {
    "id": 1,
    "time": {"begin": "00:00:00", "end": "00:00:30"},
    "name": "Speaker_Name",
    "text": "Some spoken text..."
  }
]
```

Where `MeetingEntry` has the following structure:

```typescript
interface TimeRange {
  begin: string; // Format: HH:MM:SS
  end: string;   // Format: HH:MM:SS
}

interface MeetingEntry {
  id: number;
  time: TimeRange;
  name: string;
  text: string;
}
```

**Responses:**

* **200 OK**: Successful summarization.

  ```json
  {
    "think": "...", // Thought process or intermediate steps from the model
    "result": "..." // The final summary
  }
  ```
* **500 Internal Server Error**: If an error occurs during summarization.

  ```json
  {
    "error": "generation errror",
    "message": "Error summarizing meeting: <error details>",
    "timestamp": "YYYY-MM-DDTHH:MM:SS.ffffffZ"
  }
  ```

#### `POST /summarize/file`

Summarizes a meeting transcript from an uploaded JSON file. The file should contain a list of `MeetingEntry` objects (see `/summarize/list` for structure).

**Request (**`**multipart/form-data**`**):**

* `file`: The JSON file containing meeting entries.

**Responses:**

* **200 OK**: Successful summarization.

  ```json
  {
    "think": "...",
    "result": "..."
  }
  ```
* **400 Bad Request**: Invalid JSON file.

  ```json
  {
    "detail": "Invalid JSON file"
  }
  ```
* **501 Internal Server Error**: If an error occurs during summarization.

  ```json
  {
    "error": "generation errror",
    "message": "Error summarizing meeting from file: <error details>",
    "timestamp": "YYYY-MM-DDTHH:MM:SS.ffffffZ"
  }
  ```

### Question & Answer Generation

#### `POST /qa/list`

Generates Question/Answer pairs for a meeting transcript provided as a JSON list of entries in the request body.

**Request Body (**`**application/json**`**):** Same as `/api/v1/summarize/list`.

**Responses:**

* **200 OK**: Successful Q&A generation.

  ```json
  {
    "think": "...", // Thought process or intermediate steps from the model
    "result": "..." // The generated Q&A pairs
  }
  ```
* **500 Internal Server Error**: If an error occurs during Q&A generation.

  ```json
  {
    "error": "generation errror",
    "message": "Error generating QA: <error details>",
    "timestamp": "YYYY-MM-DDTHH:MM:SS.ffffffZ"
  }
  ```

#### `POST /qa/file`

Generates Question/Answer pairs for a meeting transcript from an uploaded JSON file. The file should contain a list of `MeetingEntry` objects.

**Request (**`**multipart/form-data**`**):**

* `file`: The JSON file containing meeting entries.

**Responses:**

* **200 OK**: Successful Q&A generation.

  ```json
  {
    "think": "...",
    "result": "..."
  }
  ```
* **400 Bad Request**: Invalid JSON file.

  ```json
  {
    "detail": "Invalid JSON file"
  }
  ```
* **501 Internal Server Error**: If an error occurs during Q&A generation.

  ```json
  {
    "error": "generation errror",
    "message": "Error generating QA from file: <error details>",
    "timestamp": "YYYY-MM-DDTHH:MM:SS.ffffffZ"
  }
  ```


