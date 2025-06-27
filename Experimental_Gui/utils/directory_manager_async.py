"""Async directory manager - replicates original create_directory.py functionality"""

import asyncio
import re
from pathlib import Path
from typing import Optional


class AsyncDirectoryManager:
    """Async version of DirectoryManager from original modules/create_directory.py"""
    
    def __init__(self):
        # Exact same regex pattern as original
        self.unsafe_chars = r'[:*?"<>|$#@&%!`^(){}[\]=+~,;~\0]'
        # Same max length as original to avoid Windows issues
        self.max_folder_name_length = 90
    
    def _sanitize_folder_name(self, folder_name: str) -> str:
        """
        Sanitizes the folder name by removing unsafe characters.
        Replicates original _sanitize_folder_name method exactly.
        """
        sanitized_folder_name = re.sub(self.unsafe_chars, '', folder_name)
        return sanitized_folder_name
    
    def _truncate_folder_name(self, folder_name: str) -> str:
        """
        Truncates folder name if it exceeds max length.
        Replicates original _truncate_folder_name method exactly.
        """
        if len(folder_name) > self.max_folder_name_length:
            return folder_name[:self.max_folder_name_length]
        return folder_name
    
    def _replace_spaces_with_underscores(self, folder_name: str) -> str:
        """
        Replaces spaces with underscores.
        Replicates original _replace_spaces_with_underscores method exactly.
        """
        return folder_name.replace(" ", "_")
    
    async def create_folder(self, folder_name: str, base_path: Optional[Path] = None) -> str:
        """
        Creates a folder with sanitized name.
        Replicates original create_folder method but with async folder creation.
        
        Args:
            folder_name: Raw folder name to sanitize and create
            base_path: Optional base path, defaults to current directory
            
        Returns:
            str: The final sanitized folder name that was created
        """
        # Apply same transformations as original
        sanitized_folder_name = self._sanitize_folder_name(folder_name=folder_name)
        truncated_folder_name = self._truncate_folder_name(folder_name=sanitized_folder_name)
        replaced_spaces_folder_name = self._replace_spaces_with_underscores(folder_name=truncated_folder_name)
        
        # Create the folder path
        if base_path:
            folder_path = base_path / replaced_spaces_folder_name
        else:
            folder_path = Path(replaced_spaces_folder_name)
        
        # Create folder (exist_ok=True matches original behavior)
        folder_path.mkdir(parents=True, exist_ok=True)
        
        return replaced_spaces_folder_name
    
    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize a filename (not just folder name).
        Uses same logic as folder sanitization but for individual files.
        """
        # Remove unsafe characters
        sanitized = re.sub(self.unsafe_chars, '', filename)
        # Replace spaces with underscores
        sanitized = sanitized.replace(" ", "_")
        # Truncate if too long (leave room for file extension)
        if len(sanitized) > 200:
            name_part, ext_part = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
            max_name_len = 200 - len(ext_part) - 1 if ext_part else 200
            sanitized = name_part[:max_name_len] + ('.' + ext_part if ext_part else '')
        
        # Ensure not empty
        if not sanitized or sanitized == '.':
            sanitized = "unnamed"
            
        return sanitized


# NOTE FOR FUTURE: This AsyncDirectoryManager replicates the exact behavior
# of the original modules/create_directory.py DirectoryManager class.
# Same unsafe_chars regex, same max length, same transformation order.
# Only difference is async folder creation support.