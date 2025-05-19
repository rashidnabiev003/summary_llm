import json
import subprocess
from fastapi import HTTPException

class OllamaClient:
    def __init__(self, config_path: str = "config.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.model_name = self.config['ollama']['model_name']
        self.options = self.config['ollama']['options']

    def generate(self, prompt: str) -> str:
        """Generate text using Ollama CLI"""
        cmd = [
            "ollama", "run", self.model_name,
            "--prompt", prompt,
            "--max-tokens", str(self.options['max_tokens']),
            "--temperature", str(self.options['temperature']),
            "--json"
        ]
        
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            res.raise_for_status()
            return json.loads(res.stdout)["response"].strip()
        except (subprocess.SubprocessError, json.JSONDecodeError) as e:
            raise HTTPException(status_code=500, detail=f"Error calling Ollama: {str(e)}")

    def get_prompt(self, mode: str, transcript: str) -> str:
        """Get formatted prompt based on mode"""
        prompt_template = self.config['prompts'][mode]
        return prompt_template.format(transcript=transcript) 