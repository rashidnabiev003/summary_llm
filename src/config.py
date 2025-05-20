import json
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

class Config:
    """Configuration class for the application"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent / "src" / "configs"
        self.server_config = self._load_config("server.json")
        self.prompts_config = self._load_config("prompts.json")
        
    def _load_config(self, filename: str) -> Dict[str, Any]:
        """
        Load configuration from JSON file.
        
        Args:
            filename: Name of the configuration file
            
        Returns:
            Dict containing configuration
        """
        config_path = self.base_path / filename
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info(f"Successfully loaded configuration from {filename}")
            return config
        except Exception as e:
            logger.error(f"Error loading configuration from {filename}: {str(e)}")
            raise RuntimeError(f"Failed to load configuration from {filename}: {str(e)}")
    
    @property
    def host(self) -> str:
        """Get server host"""
        return self.server_config.get("host", "0.0.0.0")
    
    @property
    def port(self) -> int:
        """Get server port"""
        return int(self.server_config.get("port", 8000))
    
    @property
    def reload(self) -> bool:
        """Get reload setting"""
        return bool(self.server_config.get("reload", True))
    
    @property
    def workers(self) -> int:
        """Get number of workers"""
        return int(self.server_config.get("workers", 1))
    
    @property
    def log_level(self) -> str:
        """Get log level"""
        return self.server_config.get("log_level", "info")
    
    @property
    def cors_origins(self) -> list:
        """Get CORS allowed origins"""
        cors = self.server_config.get("cors", {})
        return cors.get("allow_origins", ["*"])
    
    @property
    def cors_methods(self) -> list:
        """Get CORS allowed methods"""
        cors = self.server_config.get("cors", {})
        return cors.get("allow_methods", ["*"])
    
    @property
    def cors_headers(self) -> list:
        """Get CORS allowed headers"""
        cors = self.server_config.get("cors", {})
        return cors.get("allow_headers", ["*"])
    
    def get_prompt(self, mode: str) -> str:
        """
        Get prompt by mode.
        
        Args:
            mode: Prompt mode (e.g., 'summary', 'qa')
            
        Returns:
            Prompt template string
        """
        return self.prompts_config.get(mode, "") 