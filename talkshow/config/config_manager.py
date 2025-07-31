"""Configuration management for TalkShow."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """Manages configuration for TalkShow application."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration manager.
        
        Args:
            config_path: Path to configuration file. If None, uses default.
        """
        if config_path is None:
            config_path = self._find_default_config()
        
        self.config_path = Path(config_path)
        self._config = self._load_config()
    
    def _find_default_config(self) -> str:
        """Find default configuration file."""
        # Look for config in several locations
        search_paths = [
            "config/default.yaml",
            "talkshow/config/default.yaml",
            Path(__file__).parent.parent.parent / "config" / "default.yaml"
        ]
        
        for path in search_paths:
            if Path(path).exists():
                return str(path)
        
        # Fallback to a basic configuration
        return "config/default.yaml"
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if not self.config_path.exists():
            return self._get_default_config()
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                return config or {}
        except (yaml.YAMLError, IOError) as e:
            print(f"Warning: Failed to load config from {self.config_path}: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            'parser': {
                'history_directory': 'history',
                'include_patterns': ['*.md'],
                'exclude_patterns': ['README.md', '.*']
            },
            'summarizer': {
                'rule': {
                    'max_question_length': 20,
                    'max_answer_length': 80
                },
                'llm': {
                    'provider': 'moonshot',
                    'model': 'moonshot/kimi-k2-0711-preview',
                    'api_base': 'https://api.moonshot.cn/v1',
                    'max_tokens': 150,
                    'temperature': 0.3
                }
            },
            'storage': {
                'type': 'json',
                'json': {
                    'file_path': 'data/sessions.json',
                    'backup_enabled': True
                }
            },
            'cli': {
                'output_format': 'table',
                'page_size': 20,
                'date_format': '%Y-%m-%d %H:%M:%S'
            },
            'logging': {
                'level': 'INFO'
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-separated key."""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration with environment variable overrides."""
        llm_config = self.get('summarizer.llm', {}).copy()
        
        # Override with environment variables if present
        api_key = os.getenv('MOONSHOT_API_KEY') or os.getenv('LLM_API_KEY')
        if api_key:
            llm_config['api_key'] = api_key
        
        provider = os.getenv('LLM_PROVIDER')
        if provider:
            llm_config['provider'] = provider
        
        model = os.getenv('LLM_MODEL')
        if model:
            llm_config['model'] = model
        
        # Set default values if not configured
        llm_config.setdefault('model', 'moonshot/kimi-k2-0711-preview')
        llm_config.setdefault('api_base', 'https://api.moonshot.cn/v1')
        llm_config.setdefault('max_tokens', 150)
        llm_config.setdefault('temperature', 0.3)
        
        return llm_config
    
    def get_storage_config(self) -> Dict[str, Any]:
        """Get storage configuration."""
        return self.get('storage', {})
    
    def get_parser_config(self) -> Dict[str, Any]:
        """Get parser configuration."""
        return self.get('parser', {})
    
    def reload(self) -> None:
        """Reload configuration from file."""
        self._config = self._load_config()
    
    def save(self, config_path: Optional[str] = None) -> bool:
        """Save current configuration to file."""
        path = Path(config_path) if config_path else self.config_path
        
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                yaml.dump(self._config, f, default_flow_style=False, allow_unicode=True)
            return True
        except (yaml.YAMLError, IOError) as e:
            print(f"Error saving config to {path}: {e}")
            return False