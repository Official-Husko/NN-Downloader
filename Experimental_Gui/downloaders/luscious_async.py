"""Async Luscious downloader - replicates original luscious.py functionality"""

import asyncio
import json
from pathlib import Path
from typing import Optional, Callable, Dict, Any, List
from .base_async import BaseAsyncDownloader


class LusciousDownloader(BaseAsyncDownloader):
    """Async downloader for Luscious - replicates original luscious.py"""
    
    async def download_album(self, url: str, output_dir: Path = Path("media")) -> bool:
        """
        Download album from Luscious.
        Replicates original Luscious.Fetcher method exactly.
        """
        try:
            if self.progress_callback:
                self.progress_callback("Analyzing Luscious URL...")
            
            # Parse URL exactly like original
            parts = url.split("/")
            if len(parts) < 6:
                print("Invalid Luscious URL format")
                return False
            
            # Extract title and ID based on URL type (same logic as original)
            if parts[3] == "pictures":
                title = parts[5].partition("_")[0]
                album_id = parts[5].rpartition("_")[2]
            elif parts[3] in ["album", "albums"]:
                title = parts[4].partition("_")[0] 
                album_id = parts[4].rpartition("_")[2]
            else:
                print("Unsupported Luscious URL type")
                return False
            
            if not album_id:
                print("Could not extract album ID from URL")
                return False
            
            # Create output directory
            safe_title = self.sanitize_filename(title)
            album_dir = output_dir / safe_title
            album_dir.mkdir(parents=True, exist_ok=True)
            
            if self.progress_callback:
                self.progress_callback(f"Downloading album: {title}")
            
            downloaded_count = 0
            page = 1
            
            while True:
                if self.progress_callback:
                    self.progress_callback(f"Fetching page {page}...")
                
                # Prepare GraphQL query (exact same as original)
                headers = {
                    "User-Agent": "nn-downloader/1.6 (by Official Husko on GitHub)",
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
                
                # Same GraphQL query as original
                graphql_data = {
                    "id": "6",
                    "operationName": "PictureListInsideAlbum", 
                    "query": "\n    query PictureListInsideAlbum($input: PictureListInput!) {\n  picture {\n    list(input: $input) {\n      info {\n        ...FacetCollectionInfo\n      }\n      items {\n        __typename\n        id\n        title\n        description\n        created\n        like_status\n        number_of_comments\n        number_of_favorites\n        moderation_status\n        width\n        height\n        resolution\n        aspect_ratio\n        url_to_original\n        url_to_video\n        is_animated\n        position\n        permissions\n        url\n        tags {\n          category\n          text\n          url\n        }\n        thumbnails {\n          width\n          height\n          size\n          url\n        }\n      }\n    }\n  }\n}\n    \n    fragment FacetCollectionInfo on FacetCollectionInfo {\n  page\n  has_next_page\n  has_previous_page\n  total_items\n  total_pages\n  items_per_page\n  url_complete\n}\n    ",
                    "variables": {
                        "input": {
                            "filters": [{"name": "album_id", "value": album_id}],
                            "display": "position",
                            "items_per_page": 50,
                            "page": page
                        }
                    }
                }
                
                # Make GraphQL request
                api_url = "https://members.luscious.net/graphql/nobatch/?operationName=PictureListInsideAlbum"
                
                try:
                    data = await self.post_json(api_url, graphql_data, headers=headers)
                    if data is None:
                        print(f"API request failed for page {page}")
                        break
                except Exception as e:
                    print(f"Error fetching page {page}: {e}")
                    break
                
                # Parse response
                try:
                    picture_info = data["data"]["picture"]["list"]["info"]
                    picture_items = data["data"]["picture"]["list"]["items"]
                    
                    total_pages = picture_info["total_pages"]
                    total_items = picture_info["total_items"]
                    
                    # Check if we've gone past available pages
                    if page > total_pages:
                        if self.progress_callback:
                            self.progress_callback("No more pages found")
                        break
                    
                    # Check for empty results on page 2 (error condition in original)
                    if not picture_items and page == 2:
                        print("No items found - possible error with album")
                        break
                    
                    if not picture_items:
                        break
                    
                    # Download images from this page
                    for item in picture_items:
                        image_id = item.get("id", "unknown")
                        image_title = item.get("title", f"image_{image_id}")
                        image_url = item.get("url_to_original")
                        
                        if not image_url:
                            continue
                        
                        # Get file extension
                        file_ext = image_url.rpartition(".")[2] if "." in image_url else "jpg"
                        
                        # Create safe filename (same logic as original)
                        safe_image_title = self.sanitize_filename(image_title)
                        file_path = album_dir / f"{safe_image_title}_{image_id}.{file_ext}"
                        
                        # Skip if already exists
                        if file_path.exists():
                            continue
                        
                        # Download image
                        progress_info = f"{title} - {image_title}"
                        if await self.download_file(image_url, file_path, progress_info):
                            downloaded_count += 1
                        
                        if self.progress_callback:
                            self.progress_callback(f"Downloaded {downloaded_count} images from {title}")
                        
                        # Small delay to be respectful
                        await asyncio.sleep(0.5)
                    
                    page += 1
                    
                except KeyError as e:
                    print(f"Error parsing API response: {e}")
                    break
            
            if self.progress_callback:
                self.progress_callback(f"Download complete! {downloaded_count} images saved to {album_dir}")
            
            print(f"Downloaded {downloaded_count} images to {album_dir}")
            return downloaded_count > 0
            
        except Exception as e:
            print(f"Error downloading Luscious album: {e}")
            if self.progress_callback:
                self.progress_callback(f"Error: {e}")
            return False


# Async context manager function for easy use
async def download_luscious_album(
    url: str, 
    output_dir: Path = Path("media"), 
    progress_callback: Optional[Callable] = None,
    proxy_list: Optional[List[str]] = None,
    use_proxies: bool = False
) -> bool:
    """Download an album from Luscious"""
    async with LusciousDownloader(progress_callback, proxy_list, use_proxies) as downloader:
        return await downloader.download_album(url, output_dir)


# NOTE FOR FUTURE: This LusciousDownloader replicates the exact behavior
# of the original modules/luscious.py Luscious.Fetcher method.
# Same GraphQL query, same URL parsing, same file naming, same pagination logic.