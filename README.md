# Meeting Summarizer API

A microservice for summarizing meeting transcripts using Ollama and the Qwen model.

## Features

- Summarize meeting transcripts
- Generate Q&A from meeting transcripts
- Uses Ollama with Qwen model
- Configurable prompts and server settings

## Prerequisites

- Python 3.8+
- [Ollama](https://ollama.ai/) installed
- Qwen model pulled in Ollama (`ollama pull qwen`)

## Project Structure

```
├── src/
│   ├── configs/
│   │   ├── prompts.json    # Prompt templates
│   │   └── server.json     # Server configuration
│   ├── services/
│   │   ├── __init__.py     # Services package
│   │   ├── ollama_client.py # Ollama API client
│   │   └── summarizer.py   # Summarizer service
│   ├── config.py           # Configuration loader
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

## Configuration

The service can be configured by modifying the JSON files in the `src/configs` directory:

- `prompts.json` - Contains prompt templates for different modes
- `server.json` - Contains server configuration (host, port, CORS, etc.)

1. Структура проекта
Проект организован в модульную структуру:
src/configs/ - JSON-файлы конфигурации
src/services/ - сервисные компоненты
src/config.py - загрузчик конфигурации
src/schemas.py - модели данных (Pydantic)
src/main.py - основное FastAPI приложение
2. Конфигурация (configs/ и config.py)
Файлы конфигурации:
prompts.json
Содержит шаблоны запросов к модели:
summary - шаблон для суммаризации текста встречи
qa - шаблон для генерации ответов на вопросы о встрече
server.json
Содержит настройки сервера:
Host, port, режим перезагрузки, кол-во воркеров
Настройки CORS
Класс Config (config.py):
При инициализации загружает конфигурацию из JSON-файлов
Предоставляет удобный интерфейс для доступа к настройкам через свойства (property)
Обрабатывает ошибки загрузки конфигурации
3. Модели данных (schemas.py)
Использует Pydantic для валидации и сериализации данных:
TimeRange - модель для временного диапазона (начало и конец)
MeetingEntry - модель для записи части встречи (id, время, имя, текст)
MeetingRequest - модель для запроса, содержащая список записей встречи
4. Сервисы (services/)
OllamaClient (ollama_client.py):
Взаимодействует с Ollama через командную строку (subprocess)
Получает шаблоны запросов из конфигурации
Метод generate() отправляет запрос в Ollama и возвращает ответ
Метод get_prompt() форматирует шаблон запроса текстом транскрипта
Обрабатывает различные ошибки (подпроцесса, парсинга JSON и т.д.)
SummarizerService (summarizer.py):
Использует OllamaClient для взаимодействия с моделью
Метод summarize() выполняет суммаризацию или QA в зависимости от режима
Возвращает результат с метаданными (режим, модель, длина текста)
Асинхронный (использует async/await), что позволяет обрабатывать несколько запросов одновременно
5. FastAPI приложение (main.py)
Настраивает логирование
Загружает конфигурацию
Создает экземпляр FastAPI
Добавляет middleware для CORS
Инициализирует SummarizerService
Определяет эндпоинты:
GET /health - проверка работоспособности
POST /summarize - суммаризация транскрипта встречи
POST /qa - генерация Q&A по транскрипту
6. Поток данных при обработке запроса
Клиент отправляет POST-запрос на /summarize или /qa с данными встречи.
FastAPI валидирует запрос через модель MeetingRequest.
Обработчик объединяет все записи в один текст с указанием времени и говорящего.
SummarizerService получает сформированный текст и режим.
OllamaClient форматирует шаблон запроса и отправляет его в Ollama.
Ollama с моделью Qwen генерирует ответ.
OllamaClient обрабатывает ответ и возвращает его SummarizerService.
SummarizerService добавляет метаданные и возвращает результат.
FastAPI сериализует ответ в JSON и отправляет клиенту.
7. Обработка ошибок
Используется система логирования для записи информации, предупреждений и ошибок
Ошибки обрабатываются на каждом уровне и преобразуются в HTTP-исключения с соответствующими кодами
Клиент получает информативные сообщения об ошибках
8. Особенности реализации
Модульность: каждый компонент отвечает за одну функцию
Конфигурируемость: все настройки вынесены в JSON-файлы
Расширяемость: легко добавить новые режимы или модели
Асинхронность: использование FastAPI и async/await для эффективной обработки запросов
Безопасность: проверка ввода через Pydantic, обработка ошибок на всех уровнях
Этот микросервис представляет собой хорошо структурированное решение для суммаризации текстов встреч, которое можно легко развернуть и интегрировать с другими системами.