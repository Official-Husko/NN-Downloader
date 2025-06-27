"""Async Multporn downloader - replicates original multporn.py functionality exactly"""

import asyncio
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, Callable, List
from .base_async import BaseAsyncDownloader


class MultpornDownloader(BaseAsyncDownloader):
    """Async downloader for Multporn - replicates original multporn.py exactly"""
    
    async def download_comic(self, url: str, output_dir: Path = Path("media")) -> bool:
        """Download comic from Multporn - replicates original Multporn.Fetcher exactly"""
        try:
            if self.progress_callback:
                self.progress_callback("Analyzing Multporn URL...")
            
            # URL parsing (exact same as original)
            parts = url.split("/")
            if len(parts) < 5:
                print("Invalid Multporn URL format")
                return False
                
            type_category = parts[3]
            title = parts[4]
            
            # Category mapping (exact same as original)
            if type_category in ["comics", "hentai_manga", "gay_porn_comics", "gif", "humor"]:
                field_type = "field_com_pages"
            elif type_category in ["pictures", "hentai"]:
                field_type = "field_img"
            elif type_category == "rule_63":
                field_type = "field_rule_63_img"
            elif type_category == "games":
                field_type = "field_screenshots"
            elif type_category == "video":
                print("Sorry but videos are currently not supported.")
                return False
            else:
                print("Sorry but this type is not recognized. Please open a ticket with the link.")
                return False
            
            if self.progress_callback:
                self.progress_callback(f"Fetching {title} metadata...")
            
            # Fetch main page to get item ID (same as original)
            page_content = await self.fetch_page(url)
            if not page_content:
                print("Failed to fetch main page")
                return False
            
            # Extract item ID from page (same logic as original)
            try:
                # Try to find shortlink in HTML
                pattern = r'<link\s+rel="shortlink"\s+href="([^"]+)"\s*/?>'
                match = re.search(pattern, page_content)
                
                if match:
                    raw_link = match.group(1)
                else:
                    print("Node Link not Found. Double check the link else report this.")
                    return False
                    
            except Exception as e:
                print(f"Node Link not Found. Double check the link else report this. Error: {e}")
                return False
            
            # Extract ID from link (same regex as original)
            link_match = re.findall(r"(http|https|ftp):[/]{2}([a-zA-Z0-9-.]+.[a-zA-Z]{2,4})(:[0-9]+)?/?([a-zA-Z0-9-._?,'/\+&%$#=~]*)", raw_link)
            if not link_match:
                print("Could not extract ID from shortlink")
                return False
                
            item_id = link_match[0][3]
            
            # Fetch juicebox XML (exact same URL as original)
            juicebox_url = f"https://multporn.net/juicebox/xml/field/node/{item_id}/{field_type}/full"
            
            if self.progress_callback:
                self.progress_callback("Fetching image list...")
            
            # Fetch XML content
            async with self.session.get(juicebox_url) as response:
                if response.status == 404:
                    print("An error occurred! please report this to the dev")
                    return False
                elif response.status != 200:
                    print(f"Failed to fetch juicebox XML: HTTP {response.status}")
                    return False
                
                xml_content = await response.read()
            
            # Parse XML to get image URLs (same as original structure)
            try:
                root = ET.fromstring(xml_content)
            except Exception as e:
                print(f"Failed to parse XML: {e}")
                return False
            
            # Extract image URLs from XML (same structure as original)
            images = []
            for image_elem in root.findall('image'):
                link_url = image_elem.get('linkURL')
                if link_url:
                    images.append(link_url)
            
            if not images:
                print("No images found")
                return False
            
            # Create output directory (same logic as original)
            safe_title = self.sanitize_filename(title)
            comic_dir = output_dir / safe_title
            comic_dir.mkdir(parents=True, exist_ok=True)
            
            if self.progress_callback:
                self.progress_callback(f"Downloading {len(images)} images from {title}")
            
            # Download images (same numbering as original: 1, 2, 3...)
            downloaded = 0
            for i, image_url in enumerate(images, 1):
                # Get file extension (same logic as original)
                image_format = image_url.rpartition(".")[2] or "jpg"
                file_path = comic_dir / f"{i}.{image_format}"
                
                # Skip if already exists
                if file_path.exists():
                    continue
                
                progress_info = f"{title} - Image {i}/{len(images)}"
                if await self.download_file(image_url, file_path, progress_info):
                    downloaded += 1
                
                # Update progress
                if self.progress_callback:
                    progress = int((i / len(images)) * 100)
                    self.progress_callback(f"Downloaded {i}/{len(images)} images ({progress}%)")
                
                # Small delay like original sleep(1)
                await asyncio.sleep(1)
            
            if self.progress_callback:
                self.progress_callback(f"Completed downloading {title}!")
            
            print(f"Completed downloading {title}!")
            print(f"Downloaded {downloaded} images to {comic_dir}")
            return downloaded > 0
            
        except Exception as e:
            print(f"Error downloading comic: {e}")
            if self.progress_callback:
                self.progress_callback(f"Error: {e}")
            return False


# Async context manager function for easy use
async def download_multporn_comic(
    url: str, 
    output_dir: Path = Path("media"), 
    progress_callback: Optional[Callable] = None,
    proxy_list: Optional[List[str]] = None,
    use_proxies: bool = False
) -> bool:
    """Download a comic from Multporn"""
    async with MultpornDownloader(progress_callback, proxy_list, use_proxies) as downloader:
        return await downloader.download_comic(url, output_dir)


# NOTE FOR FUTURE: This MultpornDownloader replicates the exact behavior
# of the original modules/multporn.py Multporn.Fetcher method.
# Same URL parsing, same category mapping, same ID extraction, same XML parsing,
# same file numbering (1, 2, 3...), same directory structure.