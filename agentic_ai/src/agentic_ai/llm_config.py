"""
LLM Configuration Manager for Agentic AI System

This module handles the configuration and selection of different LLM models
for different types of tasks, allowing for optimal model usage based on task complexity.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from rich.console import Console

console = Console()

class LLMConfigManager:
    """Manages LLM configuration and model selection for different agents and tasks."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the LLM configuration manager."""
        if config_path is None:
            config_path = Path(__file__).parent / "config" / "llm_config.yaml"
        
        self.config_path = config_path
        self.config = self._load_config()
        self.models = self.config.get('models', {})
        self.agent_mapping = self.config.get('agent_model_mapping', {})
        self.fallback_model = self.config.get('fallback_model', 'tinyllama')
    
    def _load_config(self) -> Dict[str, Any]:
        """Load LLM configuration from YAML file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            console.print(f"[red]ERROR: LLM config file not found at {self.config_path}[/red]")
            return {}
        except yaml.YAMLError as e:
            console.print(f"[red]ERROR: Invalid YAML in LLM config: {e}[/red]")
            return {}
    
    def get_model_for_agent(self, agent_name: str) -> str:
        """Get the appropriate model for a specific agent."""
        return self.agent_mapping.get(agent_name, self.fallback_model)
    
    def get_model_config(self, model_name: str) -> Dict[str, Any]:
        """Get configuration for a specific model."""
        return self.models.get(model_name, {})
    
    def get_llm_string(self, agent_name: str) -> str:
        """Get the LLM string for CrewAI agent initialization."""
        model_name = self.get_model_for_agent(agent_name)
        model_config = self.get_model_config(model_name)
        
        if not model_config:
            console.print(f"[yellow]WARNING: No config found for model {model_name}, using fallback[/yellow]")
            return self._get_fallback_llm_string()
        
        provider = model_config.get('provider', 'ollama')
        model_name_config = model_config.get('model_name', 'tinyllama')
        
        if provider == 'perplexity':
            # Check for API key
            api_key_env = model_config.get('api_key_env', 'PERPLEXITY_API_KEY')
            if not os.getenv(api_key_env):
                console.print(f"[yellow]WARNING: {api_key_env} not found, falling back to TinyLlama[/yellow]")
                return self._get_fallback_llm_string()
            
            return f"perplexity/{model_name_config}"
        
        elif provider == 'ollama':
            # Set API base for Ollama
            api_base = model_config.get('api_base', 'http://localhost:11434')
            os.environ['API_BASE'] = api_base
            return f"ollama/{model_name_config}"
        
        else:
            console.print(f"[yellow]WARNING: Unknown provider {provider}, using fallback[/yellow]")
            return self._get_fallback_llm_string()
    
    def _get_fallback_llm_string(self) -> str:
        """Get fallback LLM string."""
        fallback_config = self.get_model_config(self.fallback_model)
        if fallback_config:
            provider = fallback_config.get('provider', 'ollama')
            model_name = fallback_config.get('model_name', 'tinyllama')
            
            if provider == 'ollama':
                api_base = fallback_config.get('api_base', 'http://localhost:11434')
                os.environ['API_BASE'] = api_base
            
            return f"{provider}/{model_name}"
        
        # Ultimate fallback
        os.environ['API_BASE'] = 'http://localhost:11434'
        return "ollama/tinyllama"
    
    def validate_model_availability(self, model_name: str) -> bool:
        """Validate if a model is available and properly configured."""
        model_config = self.get_model_config(model_name)
        if not model_config:
            return False
        
        provider = model_config.get('provider', 'ollama')
        
        if provider == 'perplexity':
            api_key_env = model_config.get('api_key_env', 'PERPLEXITY_API_KEY')
            return bool(os.getenv(api_key_env))
        
        elif provider == 'ollama':
            # For Ollama, we assume it's running locally
            return True
        
        return False
    
    def get_available_models(self) -> Dict[str, bool]:
        """Get status of all configured models."""
        availability = {}
        for model_name in self.models.keys():
            availability[model_name] = self.validate_model_availability(model_name)
        return availability
    
    def display_model_status(self):
        """Display the status of all configured models."""
        console.print("\n[bold cyan]LLM Model Status:[/bold cyan]")
        
        availability = self.get_available_models()
        
        for model_name, is_available in availability.items():
            model_config = self.get_model_config(model_name)
            description = model_config.get('description', 'No description')
            
            status_icon = "✅" if is_available else "❌"
            status_text = "Available" if is_available else "Not Available"
            
            console.print(f"{status_icon} [bold]{model_name}[/bold]: {status_text}")
            console.print(f"   {description}")
            
            if not is_available and model_config.get('provider') == 'perplexity':
                api_key_env = model_config.get('api_key_env', 'PERPLEXITY_API_KEY')
                console.print(f"   [yellow]Missing: {api_key_env} environment variable[/yellow]")
        
        console.print(f"\n[bold]Agent Model Mapping:[/bold]")
        for agent_name, model_name in self.agent_mapping.items():
            status = "✅" if availability.get(model_name, False) else "❌"
            console.print(f"{status} {agent_name}: {model_name}")


# Global instance for easy access
llm_config = LLMConfigManager()
