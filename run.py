import sys
import os
import uvicorn

# Добавляем корневую директорию проекта в путь Python
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

if __name__ == "__main__":
    # Импортируем и запускаем приложение напрямую
    from src.main import app
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=49137,
        log_level="info",
    ) 