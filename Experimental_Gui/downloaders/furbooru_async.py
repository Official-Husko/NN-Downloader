"""Async Furbooru downloader - replicates original furbooru.py functionality"""

import asyncio
from pathlib import Path
from typing import Optional, Callable, List, Dict, Any
from datetime import datetime
from .base_async import BaseAsyncDownloader


class FurbooruDownloader(BaseAsyncDownloader):
    """Async downloader for Furbooru - replicates original furbooru.py"""
    
    def __init__(self, progress_callback: Optional[Callable] = None):
        super().__init__(progress_callback)
        self.dt_now = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    
    async def download_by_tags(
        self, 
        tags: str,
        blacklist: Optional[List[str]] = None,
        max_pages: Optional[int] = None,
        api_key: Optional[str] = None,
        db_file: Optional[str] = None,
        output_dir: Path = Path("media")
    ) -> bool:
        """
        Download images by tags from Furbooru.
        Replicates original FURBOORU.fetcher method exactly.
        """
        try:
            if self.progress_callback:
                self.progress_callback(f"Starting Furbooru download for tags: {tags}")
            
            # Format tags same as original (replace spaces with commas)
            formatted_tags = tags.replace(" ", ", ")
            blacklist = blacklist or []
            page = 1
            
            # Load existing database if specified
            downloaded_ids = set()
            if db_file:
                db_path = Path("db") / "furbooru.db"
                if db_path.exists():
                    with open(db_path, "r", encoding="utf-8") as f:
                        downloaded_ids = {line.strip() for line in f if line.strip()}
            
            while True:
                if self.progress_callback:
                    self.progress_callback(f"Fetching page {page}...")
                
                # Construct API URL (same as original)
                api_url = f"https://furbooru.org/api/v1/json/search/images?q={formatted_tags}&page={page}&per_page=50"
                if api_key:
                    api_url += f"&key={api_key}"
                
                # Prepare headers
                headers = {
                    "User-Agent": "nn-downloader/2.0 (by Official-Husko on GitHub)"
                }
                
                # Make API request
                try:
                    async with self.session.get(api_url, headers=headers) as response:
                        if response.status != 200:
                            print(f"API request failed with status {response.status}")
                            break
                        
                        data = await response.json()
                except Exception as e:
                    print(f"Error fetching page {page}: {e}")
                    break
                
                # Check if no images found (same as original)
                if data.get("total", 0) == 0:
                    if self.progress_callback:
                        self.progress_callback("No images found or all downloaded! Try different tags.")
                    print("No images found or all downloaded! Try different tags.")
                    break
                
                # Check max pages limit (same as original)
                if max_pages and page >= max_pages:
                    if self.progress_callback:
                        self.progress_callback(f"Finished downloading {max_pages} of {max_pages} pages.")
                    print(f"Finished downloading {max_pages} of {max_pages} pages.")
                    break
                
                # Process images for this page
                page_approved = []
                images = data.get("images", [])
                
                for item in images:
                    # Skip hidden images (same as original)
                    if item.get("hidden_from_users", False):
                        continue
                    
                    # Check blacklist (same as original)
                    post_tags = item.get("tags", [])
                    if any(tag in blacklist for tag in post_tags):
                        continue
                    
                    image_id = str(item["id"])
                    image_address = item.get("representations", {}).get("full")
                    image_format = item.get("format", "png")
                    
                    if not image_address:
                        continue
                    
                    # Skip if already downloaded (same logic as original)
                    if db_file and image_id in downloaded_ids:
                        continue
                    
                    # Add to approved list
                    image_data = {
                        "image_address": image_address,
                        "image_format": image_format,
                        "image_id": image_id
                    }
                    page_approved.append(image_data)
                
                # Download all approved images from this page
                if page_approved:
                    await self._download_page_images(page_approved, tags, db_file, output_dir)
                
                if self.progress_callback:
                    self.progress_callback(f"Page {page} completed")
                print(f"Page {page} completed")
                
                page += 1
                # Small delay like original
                await asyncio.sleep(1)
            
            if self.progress_callback:
                self.progress_callback(f"Download complete for tags: {tags}")
            
            print(f"Download complete for tags: {tags}")
            return True
            
        except Exception as e:
            print(f"Error downloading from Furbooru: {e}")
            if self.progress_callback:
                self.progress_callback(f"Error: {e}")
            return False
    
    async def _download_page_images(
        self, 
        approved_list: List[Dict[str, Any]], 
        tags: str,
        db_file: Optional[str],
        output_dir: Path
    ) -> None:
        """Download all images from a page (replicates original download loop)"""
        
        # Create directory (same pattern as original)
        safe_tags = self.sanitize_filename(tags).replace(" ", "_")
        directory_name = f"{self.dt_now}_{safe_tags}"
        main_dir = output_dir / directory_name
        main_dir.mkdir(parents=True, exist_ok=True)
        
        downloaded_count = 0
        total_images = len(approved_list)
        
        if self.progress_callback:
            self.progress_callback(f"Downloading {total_images} images...")
        
        for i, data in enumerate(approved_list):
            image_address = data.get("image_address")
            image_format = data.get("image_format", "png")
            image_id = data.get("image_id")
            
            if not image_address or not image_id:
                continue
            
            # Download image file
            file_path = main_dir / f"{image_id}.{image_format}"
            progress_info = f"Furbooru - Image {image_id} ({i+1}/{total_images})"
            
            if await self.download_file(image_address, file_path, progress_info):
                downloaded_count += 1
                
                # Update database file (same as original)
                if db_file:
                    db_path = Path("db")
                    db_path.mkdir(exist_ok=True)
                    db_file_path = db_path / "furbooru.db"
                    try:
                        with open(db_file_path, "a", encoding="utf-8") as db_writer:
                            db_writer.write(f"{image_id}\n")
                    except Exception as e:
                        print(f"Error updating database: {e}")
            
            if self.progress_callback:
                progress_percent = int(((i + 1) / total_images) * 100)
                self.progress_callback(f"Downloaded {i+1}/{total_images} images ({progress_percent}%)")
        
        if self.progress_callback:
            self.progress_callback(f"Downloaded {downloaded_count} images to {main_dir}")
        
        print(f"Downloaded {downloaded_count} images to {main_dir}")


# Async context manager function for easy use
async def download_furbooru_tags(
    tags: str,
    blacklist: Optional[List[str]] = None,
    max_pages: Optional[int] = None,
    api_key: Optional[str] = None,
    db_file: Optional[str] = None,
    output_dir: Path = Path("media"),
    progress_callback: Optional[Callable] = None,
    proxy_list: Optional[List[str]] = None,
    use_proxies: bool = False
) -> bool:
    """Download images by tags from Furbooru"""
    async with FurbooruDownloader(progress_callback, proxy_list, use_proxies) as downloader:
        return await downloader.download_by_tags(
            tags=tags,
            blacklist=blacklist,
            max_pages=max_pages,
            api_key=api_key,
            db_file=db_file,
            output_dir=output_dir
        )


# NOTE FOR FUTURE: This FurbooruDownloader replicates the exact behavior
# of the original modules/furbooru.py FURBOORU.fetcher method.
# Same API calls, same blacklist filtering, same database tracking,
# same directory structure, same tag formatting.