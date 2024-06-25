# Import Standard Libraries
import os
import re

# Import Third Party Libraries

# Import Local Libraries


class DirectoryManager:
    """
    A class for managing directories.

    This class provides methods for creating directories with sanitized, truncated, and space-replaced names.
    It also handles the sanitization, truncation, and space replacement of folder names.

    Attributes:
        unsafe_chars (str): A regular expression pattern that matches characters not allowed in folder names.
        max_folder_name_length (int): The maximum allowed length for folder names on Windows to avoid issues with long folder names.

    Methods:
        __init__(self) -> None: Initializes a new instance of the `DirectoryManager` class.
        _sanitize_folder_name(self, folder_name: str) -> str: Sanitizes the folder name by removing any unsafe characters.
        _truncate_folder_name(self, folder_name: str) -> str: Truncates the given folder name if it exceeds the maximum allowed length.
        _replace_spaces_with_underscores(self, folder_name: str) -> str: Replaces spaces with underscores in the given folder name.
        create_folder(self, folder_name: str) -> str: Creates a folder with the given folder name.
    """
    
    def __init__(self) -> None:
        """
        Initializes a new instance of the `DirectoryManager` class.

        This method sets the `unsafe_chars` attribute to a regular expression pattern that matches characters that are not allowed in folder names. 
        It also sets the `max_folder_name_length` attribute to 90, which is the maximum length allowed for folder names on Windows to avoid issues with long folder names.

        Parameters:
            None

        Returns:
            None
        """

        self.unsafe_chars = r'[:*?"<>|$#@&%!`^(){}[\]=+~,;~\0]'
        # I am keeping this at 90 to avoid general issues with long folder names especially on Windows
        self.max_folder_name_length = 90

    def _sanitize_folder_name(self, folder_name: str) -> str:
        """
        Sanitizes the folder name by removing unsafe characters based on the `unsafe_chars` attribute.

        Parameters:
            folder_name (str): The input folder name to be sanitized.

        Returns:
            str: The sanitized folder name.
        """

        sanitized_folder_name = re.sub(self.unsafe_chars, '', folder_name)

        return sanitized_folder_name

    def _truncate_folder_name(self, folder_name: str) -> str:
        """
        Truncates the given folder name if it exceeds the maximum allowed length.

        Parameters:
            folder_name (str): The input folder name to be truncated.

        Returns:
            str: The truncated folder name if it exceeds the maximum allowed length, 
                 otherwise the original folder name.
        """

        if len(folder_name) > self.max_folder_name_length:
            return folder_name[:self.max_folder_name_length]

        return folder_name

    def _replace_spaces_with_underscores(self, folder_name: str) -> str:
        """
        Replaces spaces with underscores in the given folder name.

        Parameters:
            folder_name (str): The input folder name with spaces to be replaced.

        Returns:
            str: The folder name with spaces replaced by underscores.
        """

        return folder_name.replace(" ", "_")

    def create_folder(self, folder_name: str) -> str:
        """
        Creates a folder with the given folder name.

        Parameters:
            folder_name (str): The name of the folder to be created.

        Returns:
            str: The sanitized, truncated, and space-replaced folder name.

        This function takes a folder name as input and performs the following steps:
        1. Sanitizes the folder name by removing any unsafe characters.
        2. Truncates the folder name if it exceeds the maximum allowed length.
        3. Replaces any spaces in the folder name with underscores.
        4. Creates the folder with the sanitized, truncated, and space-replaced name.
        5. Returns the sanitized, truncated, and space-replaced folder name.

        Note:
        - The function uses the private methods `_sanitize_folder_name`, `_truncate_folder_name`, and `_replace_spaces_with_underscores` to perform the sanitization, truncation, and space replacement respectively.
        - The `os.makedirs` function is used to create the folder with the sanitized, truncated, and space-replaced name.
        - The `exist_ok=True` parameter ensures that the function does not raise an exception if the folder already exists.
        """

        sanitized_folder_name = self._sanitize_folder_name(folder_name=folder_name)
        truncated_folder_name = self._truncate_folder_name(folder_name=sanitized_folder_name)
        replaced_spaces_folder_name = self._replace_spaces_with_underscores(folder_name=truncated_folder_name)

        os.makedirs(replaced_spaces_folder_name, exist_ok=True)

        return replaced_spaces_folder_name
