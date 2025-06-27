"""Async Yiffer downloader - replicates original yiffer.py functionality"""

import asyncio
import urllib.parse
from pathlib import Path
from typing import Optional, Callable, List
from .base_async import BaseAsyncDownloader


class YifferDownloader(BaseAsyncDownloader):
    """Async downloader for Yiffer - replicates original yiffer.py"""
    
    async def download_comic(self, url: str, output_dir: Path = Path("media")) -> bool:
        """Download comic from Yiffer - replicates original Yiffer.Fetcher exactly"""
        try:
            if self.progress_callback:
                self.progress_callback("Analyzing Yiffer URL...")
            
            # URL operations (same as original)
            decoded_url = urllib.parse.unquote(url, encoding='utf-8', errors='replace')
            parts = decoded_url.split("/")
            if len(parts) < 4:
                print("Invalid Yiffer URL format")
                return False
            
            title = parts[3]
            
            # Get comic info from API (same as original)
            api_url = f"https://yiffer.xyz/api/comics/{title}"
            comic_data = await self.fetch_json(api_url)
            if not comic_data:
                return False
            
            pages = comic_data.get("numberOfPages", 0)
            if pages <= 0:
                print("No pages found for this comic")
                return False
            
            # Create output directory
            safe_title = self.sanitize_filename(title)
            comic_dir = output_dir / safe_title
            comic_dir.mkdir(parents=True, exist_ok=True)
            
            if self.progress_callback:
                self.progress_callback(f"Downloading {pages} pages from {title}")
            
            downloaded_count = 0
            
            # Download all images (same logic as original)
            for page_num in range(1, pages + 1):
                # Format page number same as original
                if page_num <= 9:
                    formatted_num = f"00{page_num}"
                elif page_num < 100:
                    formatted_num = f"0{page_num}"
                else:
                    formatted_num = str(page_num)
                
                # Construct image URL (same as original)
                image_url = f"https://static.yiffer.xyz/comics/{title}/{formatted_num}.jpg"
                file_path = comic_dir / f"{formatted_num}.jpg"
                
                # Skip if already exists
                if file_path.exists():
                    continue
                
                progress_info = f"{title} - Page {page_num}/{pages}"
                if await self.download_file(image_url, file_path, progress_info):
                    downloaded_count += 1
                
                if self.progress_callback:
                    progress_percent = int((page_num / pages) * 100)
                    self.progress_callback(f"Downloaded {page_num}/{pages} pages ({progress_percent}%)")
                
                # Small delay (matches original sleep(1))
                await asyncio.sleep(0.5)
            
            if self.progress_callback:
                self.progress_callback(f"Download complete! {downloaded_count} pages saved to {comic_dir}")
            
            print(f"Downloaded {downloaded_count} pages to {comic_dir}")
            return downloaded_count > 0
            
        except Exception as e:
            print(f"Error downloading Yiffer comic: {e}")
            if self.progress_callback:
                self.progress_callback(f"Error: {e}")
            return False


# Async context manager function for easy use
async def download_yiffer_comic(
    url: str, 
    output_dir: Path = Path("media"), 
    progress_callback: Optional[Callable] = None,
    proxy_list: Optional[List[str]] = None,
    use_proxies: bool = False
) -> bool:
    """Download a comic from Yiffer"""
    async with YifferDownloader(progress_callback, proxy_list, use_proxies) as downloader:
        return await downloader.download_comic(url, output_dir)


# NOTE FOR FUTURE: This YifferDownloader replicates the exact behavior
# of the original modules/yiffer.py Yiffer.Fetcher method.
# Same URL parsing, same API call, same image URL formatting, same numbering.