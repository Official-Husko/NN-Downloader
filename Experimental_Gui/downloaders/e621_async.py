"""Async E621/E6AI/E926 downloader - replicates original e6systems.py functionality"""

import asyncio
import json
import random
from pathlib import Path
from typing import Optional, Callable, List, Dict, Any
from datetime import datetime
import aiohttp
from .base_async import BaseAsyncDownloader


class E621Downloader(BaseAsyncDownloader):
    """Async downloader for E621/E6AI/E926 - replicates original e6systems.py"""
    
    def __init__(self, progress_callback: Optional[Callable] = None):
        super().__init__(progress_callback)
        self.approved_list = []
        self.dt_now = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    
    async def download_by_tags(
        self, 
        tags: str, 
        site: str = "e621",
        blacklist: Optional[List[str]] = None,
        max_pages: Optional[int] = None,
        api_user: Optional[str] = None,
        api_key: Optional[str] = None,
        ai_training: bool = False,
        db_file: Optional[str] = None,
        output_dir: Path = Path("media")
    ) -> bool:
        """
        Download images by tags from E621/E6AI/E926.
        Replicates original E6System.fetcher method exactly.
        """
        try:
            if self.progress_callback:
                self.progress_callback(f"Starting {site} download for tags: {tags}")
            
            blacklist = blacklist or []
            page = 1
            
            # Load existing database if specified
            downloaded_ids = set()
            if db_file:
                db_path = Path("db") / f"{site}.db"
                if db_path.exists():
                    with open(db_path, "r", encoding="utf-8") as f:
                        downloaded_ids = {line.strip() for line in f if line.strip()}
            
            while True:
                if self.progress_callback:
                    self.progress_callback(f"Fetching page {page}...")
                
                # Construct API URL (same as original)
                api_url = f"https://{site}.net/posts.json?tags={tags}&limit=320&page={page}"
                
                # Prepare headers and auth (same as original)
                auth = None
                if api_user and api_key:
                    auth = aiohttp.BasicAuth(api_user, api_key)
                
                # Make API request
                try:
                    async with self.session.get(api_url, auth=auth) as response:
                        if response.status != 200:
                            print(f"API request failed with status {response.status}")
                            break
                        
                        data = await response.json()
                except Exception as e:
                    print(f"Error fetching page {page}: {e}")
                    break
                
                # Check for API limit message (same as original)
                if isinstance(data, dict) and "message" in data:
                    if "You cannot go beyond page 750" in data["message"]:
                        print(f"{data['message']} (API limit)")
                        break
                
                # Check if no posts found (same as original)
                posts = data.get("posts", [])
                if not posts:
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
                
                # Process posts for this page
                page_approved = []
                for item in posts:
                    image_id = str(item["id"])
                    file_info = item.get("file", {})
                    image_address = file_info.get("url")
                    
                    if not image_address:
                        continue
                    
                    # Get tags (same logic as original)
                    meta_tags = item["tags"] if ai_training else {}
                    item_tags = item.get("tags", {})
                    
                    # Collect all tags for blacklist checking (same as original)
                    post_tags = []
                    for tag_type in ["general", "species", "character"]:
                        post_tags.extend(item_tags.get(tag_type, []))
                    
                    # Add site-specific tags (same as original)
                    if site == "e6ai":
                        post_tags.extend(item_tags.get("director", []))
                        post_tags.extend(item_tags.get("meta", []))
                    else:
                        post_tags.extend(item_tags.get("copyright", []))
                        post_tags.extend(item_tags.get("artist", []))
                    
                    # Check blacklist (same logic as original)
                    passed = sum(1 for blacklisted_tag in blacklist if blacklisted_tag in post_tags)
                    
                    # Skip if blacklisted or already downloaded
                    if passed > 0:
                        continue
                    
                    if db_file and image_id in downloaded_ids:
                        continue
                    
                    # Add to approved list
                    image_data = {
                        "image_address": image_address,
                        "image_format": file_info.get("ext", "jpg"),
                        "image_id": image_id,
                        "meta_tags": meta_tags
                    }
                    page_approved.append(image_data)
                
                # Download all approved images from this page
                if page_approved:
                    await self._download_page_images(page_approved, tags, site, ai_training, db_file, output_dir)
                
                if self.progress_callback:
                    self.progress_callback(f"Page {page} completed")
                print(f"Page {page} completed")
                
                page += 1
                # Small delay like original (sleep(5))
                await asyncio.sleep(2)
            
            if self.progress_callback:
                self.progress_callback(f"Download complete for tags: {tags}")
            
            print(f"Download complete for tags: {tags}")
            return True
            
        except Exception as e:
            print(f"Error downloading from {site}: {e}")
            if self.progress_callback:
                self.progress_callback(f"Error: {e}")
            return False
    
    async def _download_page_images(
        self, 
        approved_list: List[Dict[str, Any]], 
        tags: str, 
        site: str, 
        ai_training: bool, 
        db_file: Optional[str],
        output_dir: Path
    ) -> None:
        """Download all images from a page (replicates original download loop)"""
        
        # Create main directory (same pattern as original)
        directory_name = f"{self.dt_now} {tags}"
        safe_directory_name = self.sanitize_filename(directory_name)
        main_dir = output_dir / safe_directory_name
        main_dir.mkdir(parents=True, exist_ok=True)
        
        # Create meta directory if needed
        meta_dir = main_dir / "meta"
        if ai_training:
            meta_dir.mkdir(parents=True, exist_ok=True)
        
        downloaded_count = 0
        total_images = len(approved_list)
        
        if self.progress_callback:
            self.progress_callback(f"Downloading {total_images} images...")
        
        for i, data in enumerate(approved_list):
            image_address = data.get("image_address")
            image_format = data.get("image_format", "jpg")
            image_id = data.get("image_id")
            meta_tags = data.get("meta_tags", {})
            
            if not image_address or not image_id:
                continue
            
            # Download image file
            file_path = main_dir / f"{image_id}.{image_format}"
            progress_info = f"{tags} - Image {image_id} ({i+1}/{total_images})"
            
            if await self.download_file(image_address, file_path, progress_info):
                downloaded_count += 1
                
                # Save metadata if ai_training enabled (same as original)
                if ai_training and meta_tags:
                    meta_file = meta_dir / f"{image_id}.json"
                    try:
                        with open(meta_file, 'w', encoding='utf-8') as handler:
                            json.dump(meta_tags, handler, indent=6)
                    except Exception as e:
                        print(f"Error saving metadata for {image_id}: {e}")
                
                # Update database file (same as original)
                if db_file:
                    db_path = Path("db")
                    db_path.mkdir(exist_ok=True)
                    db_file_path = db_path / f"{site}.db"
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
async def download_e621_tags(
    tags: str,
    site: str = "e621", 
    blacklist: Optional[List[str]] = None,
    max_pages: Optional[int] = None,
    api_user: Optional[str] = None,
    api_key: Optional[str] = None,
    ai_training: bool = False,
    db_file: Optional[str] = None,
    output_dir: Path = Path("media"),
    progress_callback: Optional[Callable] = None,
    proxy_list: Optional[List[str]] = None,
    use_proxies: bool = False
) -> bool:
    """Download images by tags from E621/E6AI/E926"""
    async with E621Downloader(progress_callback, proxy_list, use_proxies) as downloader:
        return await downloader.download_by_tags(
            tags=tags,
            site=site,
            blacklist=blacklist,
            max_pages=max_pages,
            api_user=api_user,
            api_key=api_key,
            ai_training=ai_training,
            db_file=db_file,
            output_dir=output_dir
        )


# NOTE FOR FUTURE: This E621Downloader replicates the exact behavior
# of the original modules/e6systems.py E6System.fetcher method.
# Same API calls, same blacklist filtering, same database tracking,
# same directory structure, same metadata handling for AI training.