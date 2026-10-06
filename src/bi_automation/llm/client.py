import json
import logging
import urllib.request
import urllib.error
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class OllamaClient:
    """Client for local Ollama server."""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 11434):
        self.base_url = f"http" + "://" + f"{host}:{port}/api"
        
    def check_health(self) -> bool:
        """Check if Ollama is running and accessible."""
        try:
            req = urllib.request.Request(f"{self.base_url}/tags", method="GET")
            with urllib.request.urlopen(req, timeout=5) as response:
                return response.status == 200
        except Exception as e:
            logger.warning(f"Ollama health check failed: {e}")
            return False

    def generate(self, prompt: str, model: str = "llama3", schema: Optional[Dict[str, Any]] = None, temperature: float = 0.0) -> Dict[str, Any]:
        """
        Generate a response constrained by JSON schema.
        """
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "seed": 42
            }
        }
        
        if schema:
            payload["format"] = schema
            
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(f"{self.base_url}/generate", data=data, method="POST")
        req.add_header("Content-Type", "application/json")
        
        try:
            with urllib.request.urlopen(req, timeout=300) as response:
                if response.status != 200:
                    raise RuntimeError(f"Ollama returned {response.status}")
                
                resp_body = response.read().decode("utf-8")
                resp_json = json.loads(resp_body)
                
                # Try to parse the response text as JSON if schema was provided
                response_text = resp_json.get("response", "")
                if schema:
                    try:
                        return json.loads(response_text)
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse Ollama JSON response: {response_text}")
                        raise RuntimeError(f"Invalid JSON from LLM: {e}")
                
                return {"text": response_text}
                
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise RuntimeError(f"LLM Generation failed: {e}")
