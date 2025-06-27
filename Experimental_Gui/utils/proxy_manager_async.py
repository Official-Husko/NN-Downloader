"""Async proxy manager - replicates original proxyScraper.py functionality"""

import asyncio
import aiohttp
import random
from typing import List, Dict, Optional


class AsyncProxyManager:
    """Async version of ProxyScraper from original modules/proxyScraper.py"""
    
    def __init__(self):
        # Exact same proxy sources as original
        self.proxy_source_list = [
            "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
            "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt", 
            "https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt",
            "https://raw.githubusercontent.com/Volodichev/proxy-list/main/http.txt",
            "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
            "https://raw.githubusercontent.com/roma8ok/proxy-list/main/proxy-list-http.txt"
        ]
        self.proxy_list = []
    
    async def scrape_proxies(self) -> List[Dict[str, str]]:
        """
        Scrape proxies from sources.
        Replicates original ProxyScraper.Scraper method with async HTTP requests.
        
        Returns:
            List of proxy dictionaries in format {"http": "proxy_url"}
        """
        self.proxy_list = []
        headers = {"User-Agent": "nn-downloader/2.0 (by Official-Husko on GitHub)"}
        
        async with aiohttp.ClientSession(headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as session:
            for source in self.proxy_source_list:
                try:
                    async with session.get(source) as response:
                        if response.status == 200:
                            proxy_raw = await response.text()
                            split_proxies = proxy_raw.split()
                            
                            for proxy in split_proxies:
                                proxy_dict = {"http": proxy.strip()}
                                # Avoid duplicates (matches original logic)
                                if proxy_dict not in self.proxy_list:
                                    self.proxy_list.append(proxy_dict)
                                    
                except Exception as e:
                    print(f"Failed to fetch proxies from {source}: {e}")
                    continue
        
        return self.proxy_list
    
    def get_random_proxy(self) -> Optional[Dict[str, str]]:
        """
        Get a random proxy from the list.
        Replicates original random.choice(proxy_list) behavior.
        
        Returns:
            Random proxy dict or None if no proxies available
        """
        if not self.proxy_list:
            return None
        return random.choice(self.proxy_list)
    
    def get_proxy_count(self) -> int:
        """Get number of available proxies"""
        return len(self.proxy_list)
    
    async def test_proxy(self, proxy: Dict[str, str], test_url: str = "http://httpbin.org/ip") -> bool:
        """
        Test if a proxy is working.
        
        Args:
            proxy: Proxy dict in format {"http": "proxy_url"}
            test_url: URL to test proxy against
            
        Returns:
            True if proxy works, False otherwise
        """
        try:
            timeout = aiohttp.ClientTimeout(total=5)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(test_url, proxy=proxy["http"]) as response:
                    return response.status == 200
        except:
            return False
    
    async def get_working_proxies(self, max_test: int = 10) -> List[Dict[str, str]]:
        """
        Test proxies and return only working ones.
        
        Args:
            max_test: Maximum number of proxies to test
            
        Returns:
            List of working proxy dictionaries
        """
        if not self.proxy_list:
            await self.scrape_proxies()
        
        working_proxies = []
        test_proxies = self.proxy_list[:max_test]
        
        for proxy in test_proxies:
            if await self.test_proxy(proxy):
                working_proxies.append(proxy)
                
        return working_proxies


# NOTE FOR FUTURE: This AsyncProxyManager replicates the exact functionality
# of the original modules/proxyScraper.py ProxyScraper class.
# Same proxy sources, same User-Agent, same proxy format.
# Added async HTTP requests and optional proxy testing functionality.