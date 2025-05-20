from setuptools import setup, find_packages

setup(
    name="summary_llm",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.104.1",
        "uvicorn==0.24.0",
        "pydantic==2.5.2",
        "python-dotenv==1.0.0",
        "ollama==0.1.6",
    ],
) 