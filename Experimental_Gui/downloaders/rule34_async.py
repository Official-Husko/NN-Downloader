"""Async Rule34 downloader"""

import asyncio
from pathlib import Path
from typing import Optional, Callable, List
from .base_async import BaseAsyncDownloader


class Rule34Downloader(BaseAsyncDownloader):
    """Async downloader for Rule34"""
    
    async def download_by_tags(self, tags: str, max_pages: Optional[int] = None, output_dir: Path = Path("media")) -> bool:
        """Download images by tags from Rule34"""
        try:
            if self.progress_callback:
                self.progress_callback("Starting Rule34 download...")
            
            # Create output directory
            safe_tags = self.sanitize_filename(tags) or "all"
            download_dir = output_dir / "rule34" / safe_tags
            download_dir.mkdir(parents=True, exist_ok=True)
            
            downloaded_count = 0
            page = 1
            
            while True:
                if max_pages and page > max_pages:
                    break
                
                if self.progress_callback:
                    self.progress_callback(f"Fetching page {page}...")
                
                # Construct API URL (same as original)
                api_url = f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&pid={page}&limit=1000&json=1&tags={tags}"
                
                # Fetch page data
                data = await self.fetch_json(api_url)
                if not data:
                    break
                
                if not isinstance(data, list) or len(data) == 0:
                    if self.progress_callback:
                        self.progress_callback("No more images found")
                    break
                
                if self.progress_callback:
                    self.progress_callback(f"Found {len(data)} images on page {page}")
                
                # Download images from this page
                for i, item in enumerate(data):
                    if "file_url" not in item or "id" not in item:
                        continue
                    
                    image_url = item["file_url"]
                    image_id = item["id"]
                    
                    # Get file extension from image name like original
                    if "image" in item:
                        image_name = item["image"]
                        file_ext = image_name.split(".")[-1] if "." in image_name else "jpg"
                    else:
                        file_ext = image_url.split(".")[-1] if "." in image_url else "jpg"
                    
                    file_path = download_dir / f"{image_id}.{file_ext}"
                    
                    # Skip if already downloaded
                    if file_path.exists():
                        continue
                    
                    progress_info = f"Rule34 - Page {page} - Image {i + 1}/{len(data)}"
                    if await self.download_file(image_url, file_path, progress_info):
                        downloaded_count += 1
                    
                    if self.progress_callback:
                        self.progress_callback(f"Downloaded {downloaded_count} images so far...")
                    
                    # Small delay to be respectful
                    await asyncio.sleep(0.3)
                
                page += 1
                
                # Break if we didn't get a full page (likely the last page)
                if len(data) < 1000:
                    break
            
            if self.progress_callback:
                self.progress_callback(f"Download complete! {downloaded_count} images saved to {download_dir}")
            
            print(f"Downloaded {downloaded_count} images to {download_dir}")
            return downloaded_count > 0
            
        except Exception as e:
            print(f"Error downloading from Rule34: {e}")
            if self.progress_callback:
                self.progress_callback(f"Error: {e}")
            return False


# Async context manager function for easy use
async def download_rule34_tags(
    tags: str, 
    blacklist: Optional[List[str]] = None,
    max_pages: Optional[int] = None, 
    db_file: Optional[str] = None,
    output_dir: Path = Path("media"), 
    progress_callback: Optional[Callable] = None,
    proxy_list: Optional[List[str]] = None,
    use_proxies: bool = False
) -> bool:
    """Download images by tags from Rule34"""
    async with Rule34Downloader(progress_callback, proxy_list, use_proxies) as downloader:
        return await downloader.download_by_tags(tags, max_pages, output_dir)