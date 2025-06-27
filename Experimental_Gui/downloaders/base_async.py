"""Base async downloader class"""

import aiohttp
import aiofiles
import asyncio
import random
from pathlib import Path
from typing import List, Optional, Callable, Dict, Any
import re


class BaseAsyncDownloader:
    """Base class for async downloaders"""
    
    def __init__(self, progress_callback: Optional[Callable] = None, proxy_list: Optional[List[str]] = None, use_proxies: bool = False):
        self.progress_callback = progress_callback
        self.session = None
        self.proxy_list = proxy_list or []
        self.use_proxies = use_proxies and len(self.proxy_list) > 0
        self.current_proxy_index = 0
        
    def _get_proxy(self) -> Optional[str]:
        """Get next proxy from list if using proxies"""
        if not self.use_proxies or not self.proxy_list:
            return None
        
        # Rotate through proxies
        proxy = self.proxy_list[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxy_list)
        return proxy
    
    async def __aenter__(self):
        connector = None
        if self.use_proxies:
            # Create connector with proxy support
            connector = aiohttp.TCPConnector(limit=10)
        
        self.session = aiohttp.ClientSession(
            headers={"User-Agent": "nn-downloader/1.6 (by Official Husko on GitHub)"},
            timeout=aiohttp.ClientTimeout(total=30),
            connector=connector
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe file system usage"""
        # Remove unsafe characters
        unsafe_chars = ["/", "\\", ":", "*", "?", "\"", "<", ">", "|", "\0", "$", "#", "@", "&", "%", "!", "`", "^", "(", ")", "{", "}", "[", "]", "=", "+", "~", ",", ";"]
        safe_name = filename
        for char in unsafe_chars:
            safe_name = safe_name.replace(char, "_")
        
        # Replace spaces with underscores
        safe_name = safe_name.replace(" ", "_")
        
        # Remove leading/trailing dots and spaces
        safe_name = safe_name.strip(". ")
        
        # Ensure it's not empty
        if not safe_name:
            safe_name = "unnamed"
            
        return safe_name
    
    async def download_file(self, url: str, file_path: Path, progress_info: str = "") -> bool:
        """Download a single file with proxy support"""
        try:
            if self.progress_callback:
                self.progress_callback(f"Downloading: {progress_info}")
            
            # Get proxy if using proxies
            proxy = self._get_proxy()
            
            async with self.session.get(url, proxy=proxy) as response:
                if response.status == 200:
                    # Create directory if it doesn't exist
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    async with aiofiles.open(file_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            await f.write(chunk)
                    
                    return True
                else:
                    print(f"Failed to download {url}: HTTP {response.status}")
                    return False
                    
        except Exception as e:
            print(f"Error downloading {url}: {e}")
            return False
    
    async def fetch_page(self, url: str, **kwargs) -> Optional[str]:
        """Fetch a web page with proxy support"""
        try:
            proxy = self._get_proxy()
            async with self.session.get(url, proxy=proxy, **kwargs) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    print(f"Failed to fetch {url}: HTTP {response.status}")
                    return None
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    async def fetch_json(self, url: str, **kwargs) -> Optional[dict]:
        """Fetch JSON data with proxy support"""
        try:
            proxy = self._get_proxy()
            async with self.session.get(url, proxy=proxy, **kwargs) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"Failed to fetch JSON {url}: HTTP {response.status}")
                    return None
        except Exception as e:
            print(f"Error fetching JSON {url}: {e}")
            return None
    
    async def post_json(self, url: str, data: Dict[str, Any], **kwargs) -> Optional[dict]:
        """Post JSON data with proxy support"""
        try:
            proxy = self._get_proxy()
            async with self.session.post(url, json=data, proxy=proxy, **kwargs) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"Failed to post to {url}: HTTP {response.status}")
                    return None
        except Exception as e:
            print(f"Error posting to {url}: {e}")
            return None