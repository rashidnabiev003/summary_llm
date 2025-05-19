import json
import requests
from fastapi import HTTPException

class OllamaClient:
    def __init__(self, config_path: str = "config.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.api_url = self.config['ollama']['api_url']
        self.model_name = self.config['ollama']['model_name']
        self.options = self.config['ollama']['options']

    def generate(self, prompt: str) -> str:
        """Generate text using Ollama API"""
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": self.options
        }
        
        try:
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()
            return response.json()["response"].strip()
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Error calling Ollama API: {str(e)}")

    def get_prompt(self, mode: str, transcript: str) -> str:
        """Get formatted prompt based on mode"""
        prompt_template = self.config['prompts'][mode]
        return prompt_template.format(transcript=transcript) 