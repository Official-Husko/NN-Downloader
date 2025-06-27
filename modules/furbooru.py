import requests  # Importing requests library for making HTTP requests
import random  # Importing random library for random selection
from termcolor import colored  # Importing colored function from termcolor for colored output
from alive_progress import alive_bar  # Importing alive_bar from alive_progress for progress bar
from time import sleep  # Importing sleep function from time for delaying execution
from datetime import datetime  # Importing datetime class from datetime module for date and time operations
import os  # Importing os module for operating system related functionalities

from main import unsafe_chars  # Importing unsafe_chars from main module

now = datetime.now()  # Getting current date and time
dt_now = now.strftime("%d-%m-%Y_%H-%M-%S")  # Formatting current date and time

class FURBOORU():
    @staticmethod
    def fetcher(user_tags, user_blacklist, proxy_list, max_sites, user_proxies, api_key, header, db):
        """
        Fetches images from Furbooru API based on user-defined tags and parameters.

        Args:
            user_tags (str): User-defined tags for image search.
            user_blacklist (list): List of tags to blacklist.
            proxy_list (list): List of proxies to use for requests.
            max_sites (int): Maximum number of pages to fetch images from.
            user_proxies (bool): Flag indicating whether to use proxies for requests.
            api_key (str): API key for accessing the Furbooru API.
            header (dict): HTTP header for requests.
            db (bool or set): Database of downloaded images.

        Returns:
            dict: Dictionary containing status of the operation.
        """
        try:
            user_tags = user_tags.replace(" ", ", ")  # Replace spaces in user_tags with commas
            approved_list = []  # List to store approved images
            page = 1  # Starting page number
            
            while True:
                URL = f"https://furbooru.org/api/v1/json/search/images?q={user_tags}&page={page}&key={api_key}&per_page=50"
                # Constructing URL for API request
                proxy = random.choice(proxy_list) if user_proxies else None  # Selecting random proxy if user_proxies is True
                raw_req = requests.get(URL, headers=header, proxies=proxy)  # Making HTTP GET request
                req = raw_req.json()  # Parsing JSON response

                if req["total"] == 0:
                    print(colored("No images found or all downloaded! Try different tags.", "yellow"))  # Display message if no images found
                    sleep(5)  # Wait for 5 seconds
                    break
                elif page == max_sites:
                    print(colored(f"Finished Downloading {max_sites} of {max_sites} pages.", "yellow"))  # Display message when maximum pages reached
                    sleep(5)  # Wait for 5 seconds
                    break
                else:
                    for item in req["images"]:
                        if not item["hidden_from_users"]:
                            post_tags = item["tags"]
                            if any(tag in user_blacklist for tag in post_tags):
                                continue  # Skip image if any blacklisted tag is found
                            
                            image_address = item["representations"]["full"]
                            image_format = item["format"]
                            image_id = item["id"]
                            
                            if db is False or str(image_id) not in db:
                                image_data = {"image_address": image_address, "image_format": image_format, "image_id": image_id}
                                approved_list.append(image_data)

                    with alive_bar(len(approved_list), calibrate=1, dual_line=True, title='Downloading') as bar:
                        for data in approved_list:
                            image_address = data["image_address"]
                            image_format = data["image_format"]
                            image_id = data["image_id"]
                            bar.text = f'-> Downloading: {image_id}, please wait...'
                            
                            proxy = random.choice(proxy_list) if user_proxies else None
                            img_data = requests.get(image_address, proxies=proxy).content if user_proxies else requests.get(image_address).content

                            safe_user_tags = "".join(char for char in user_tags if char not in unsafe_chars).replace(" ", "_")
                            directory = f"media/{dt_now}_{safe_user_tags}"
                            os.makedirs(directory, exist_ok=True)

                            with open(f"{directory}/{str(image_id)}.{image_format}", 'wb') as handler:
                                handler.write(img_data)

                            if db != False:
                                with open("db/furbooru.db", "a") as db_writer:
                                    db_writer.write(f"{str(image_id)}\n")

                            bar()
                    print(colored(f"Page {page} Completed", "green"))  # Display completion message for current page
                    approved_list.clear()  # Clear approved_list for next page
                    page += 1  # Move to next page

            return {"status": "ok"}  # Return success status

        except Exception as e:
            return {"status": "error", "uinput": user_tags, "exception": str(e), "extra": raw_req.content}  # Return error status along with details
