"""Async config manager - maintains compatibility with original config.json format"""

import json
import asyncio
import aiofiles
from pathlib import Path
from typing import Dict, Any, Optional, List


class AsyncConfigManager:
    """Async version of Config_Manager from original modules/configManager.py"""
    
    def __init__(self, config_path: Path = Path("config.json")):
        self.config_path = config_path
        self.default_version = 1.6
        
    async def create_default_config(self) -> Dict[str, Any]:
        """Create default config matching original configManager.py format"""
        default_config = {
            "version": self.default_version,
            "proxies": True,
            "checkForUpdates": True,
            "oneTimeDownload": True,
            "advancedMode": False,
            "ai_training": False,
            "user_credentials": {
                "e621": {
                    "apiUser": "",
                    "apiKey": ""
                },
                "e6ai": {
                    "apiUser": "",
                    "apiKey": ""
                },
                "e926": {
                    "apiUser": "",
                    "apiKey": ""
                },
                "furbooru": {
                    "apiKey": ""
                }
            },
            "blacklisted_tags": [
                "example1",
                "example2"
            ],
            "blacklisted_formats": [
                "example1",
                "example2"
            ]
        }
        
        # Write config file
        async with aiofiles.open(self.config_path, "w") as f:
            await f.write(json.dumps(default_config, indent=6))
            
        return default_config
    
    async def load_config(self) -> Dict[str, Any]:
        """Load config from file, create default if missing"""
        if not self.config_path.exists():
            return await self.create_default_config()
        
        try:
            async with aiofiles.open(self.config_path, "r") as f:
                content = await f.read()
                return json.loads(content)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading config: {e}")
            print("Creating new default config...")
            return await self.create_default_config()
    
    async def save_config(self, config: Dict[str, Any]) -> bool:
        """Save config to file"""
        try:
            async with aiofiles.open(self.config_path, "w") as f:
                await f.write(json.dumps(config, indent=6))
            return True
        except IOError as e:
            print(f"Error saving config: {e}")
            return False
    
    def get_api_credentials(self, config: Dict[str, Any], site: str) -> Dict[str, str]:
        """Get API credentials for a site"""
        user_creds = config.get("user_credentials", {})
        site_creds = user_creds.get(site, {})
        
        if site in ["e621", "e6ai", "e926"]:
            return {
                "api_user": site_creds.get("apiUser", ""),
                "api_key": site_creds.get("apiKey", "")
            }
        elif site == "furbooru":
            return {
                "api_key": site_creds.get("apiKey", "")
            }
        else:
            return {}
    
    def has_valid_credentials(self, config: Dict[str, Any], site: str) -> bool:
        """Check if site has valid credentials"""
        creds = self.get_api_credentials(config, site)
        
        if site in ["e621", "e6ai", "e926"]:
            return bool(creds.get("api_user") and creds.get("api_key"))
        elif site == "furbooru":
            return bool(creds.get("api_key"))
        else:
            return True  # Sites that don't need credentials
    
    def get_blacklisted_tags(self, config: Dict[str, Any]) -> List[str]:
        """Get blacklisted tags list"""
        return config.get("blacklisted_tags", [])
    
    def get_blacklisted_formats(self, config: Dict[str, Any]) -> List[str]:
        """Get blacklisted formats list"""
        return config.get("blacklisted_formats", [])
    
    def is_proxies_enabled(self, config: Dict[str, Any]) -> bool:
        """Check if proxies are enabled"""
        return config.get("proxies", False)
    
    def is_one_time_download_enabled(self, config: Dict[str, Any]) -> bool:
        """Check if one-time download (duplicate detection) is enabled"""
        return config.get("oneTimeDownload", True)
    
    def is_ai_training_mode(self, config: Dict[str, Any]) -> bool:
        """Check if AI training mode is enabled"""
        return config.get("ai_training", False)


# NOTE FOR FUTURE: This AsyncConfigManager replicates the exact functionality 
# of the original modules/configManager.py but with async file operations.
# It maintains the same config.json format for compatibility.