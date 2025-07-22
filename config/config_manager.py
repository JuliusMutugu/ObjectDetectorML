"""
Configuration management utilities.
This module follows the Single Responsibility Principle by focusing
solely on configuration loading and management.
"""
import yaml
import os
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigManager:
    """
    Manages configuration loading and access.
    
    This class follows the Single Responsibility Principle by focusing
    solely on configuration management.
    """
    
    def __init__(self, config_dir: str = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_dir: Directory containing configuration files
        """
        if config_dir is None:
            # Default to config directory relative to this file
            self.config_dir = Path(__file__).parent
        else:
            self.config_dir = Path(config_dir)
        
        self._configs: Dict[str, Dict[str, Any]] = {}
    
    def load_config(self, config_name: str) -> Dict[str, Any]:
        """
        Load a configuration file.
        
        Args:
            config_name: Name of the configuration file (without extension)
            
        Returns:
            Dict[str, Any]: Configuration data
            
        Raises:
            FileNotFoundError: If configuration file doesn't exist
            yaml.YAMLError: If configuration file is invalid YAML
        """
        if config_name in self._configs:
            return self._configs[config_name]
        
        config_path = self.config_dir / f"{config_name}.yaml"
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                config_data = yaml.safe_load(file)
                self._configs[config_name] = config_data
                return config_data
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Invalid YAML in {config_path}: {e}")
    
    def get_config(self, config_name: str, key_path: str = None) -> Any:
        """
        Get configuration value by key path.
        
        Args:
            config_name: Name of the configuration
            key_path: Dot-separated path to the configuration value (e.g., "camera.width")
            
        Returns:
            Any: Configuration value
            
        Raises:
            KeyError: If key path doesn't exist
        """
        config = self.load_config(config_name)
        
        if key_path is None:
            return config
        
        keys = key_path.split('.')
        value = config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                raise KeyError(f"Key path '{key_path}' not found in configuration '{config_name}'")
        
        return value
    
    def get_detection_config(self) -> Dict[str, Any]:
        """
        Get detection configuration.
        
        Returns:
            Dict[str, Any]: Detection configuration
        """
        return self.load_config("detection_config")
    
    def get_color_config(self) -> Dict[str, Any]:
        """
        Get color configuration.
        
        Returns:
            Dict[str, Any]: Color configuration
        """
        return self.load_config("color_config")
    
    def reload_config(self, config_name: str) -> Dict[str, Any]:
        """
        Reload a configuration file (useful for runtime updates).
        
        Args:
            config_name: Name of the configuration to reload
            
        Returns:
            Dict[str, Any]: Reloaded configuration data
        """
        if config_name in self._configs:
            del self._configs[config_name]
        return self.load_config(config_name)
    
    def save_config(self, config_name: str, config_data: Dict[str, Any]) -> None:
        """
        Save configuration data to file.
        
        Args:
            config_name: Name of the configuration file
            config_data: Configuration data to save
        """
        config_path = self.config_dir / f"{config_name}.yaml"
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as file:
            yaml.dump(config_data, file, default_flow_style=False, indent=2)
        
        # Update cached config
        self._configs[config_name] = config_data
