import requests
import random
from termcolor import colored
from alive_progress import alive_bar
from time import sleep
from datetime import datetime
import os

from main import unsafe_chars

now = datetime.now()
dt_now = now.strftime("%d-%m-%Y_%H-%M-%S")

class RULE34():
    @staticmethod
    def fetcher(user_tags, user_blacklist, proxy_list, max_sites, user_proxies, header, db):
        try:
            approved_list = []
            page = 0
            
            while True:
                URL = f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&pid={page}&limit=1000&json=1&tags={user_tags}"
                proxy = random.choice(proxy_list) if user_proxies else None
                raw_req = requests.get(URL, headers=header, proxies=proxy)
                req = raw_req.json()
                
                if not req:
                    print(colored("No images found or all downloaded! Try different tags.", "yellow"))
                    sleep(5)
                    break
                elif page == max_sites:
                    print(colored(f"Finished Downloading {max_sites} of {max_sites} pages.", "yellow"))
                    sleep(5)
                    break
                else: 
                    for item in req:
                        post_tags = str.split(item["tags"])
                        if any(tag in user_blacklist for tag in post_tags):
                            continue  # Skip image if any blacklisted tag is found

                        image_address = item["file_url"]
                        image_name = item["image"]
                        image_id = item["id"]

                        if db is False or str(image_id) not in db:
                            image_data = {"image_address": image_address, "image_name": image_name, "image_id": image_id}
                            approved_list.append(image_data)

                    with alive_bar(len(approved_list), calibrate=1, dual_line=True, title='Downloading') as bar:
                        for data in approved_list:
                            image_address = data["image_address"]
                            image_name = data["image_name"]
                            image_id = data["image_id"]
                            image_format = image_address.rpartition(".")
                            bar.text = f'-> Downloading: {image_id}, please wait...'
                            
                            proxy = random.choice(proxy_list) if user_proxies else None
                            img_data = requests.get(image_address, proxies=proxy).content if user_proxies else requests.get(image_address).content

                            safe_user_tags = user_tags.replace(" ", "_")
                            for char in unsafe_chars:
                                safe_user_tags = safe_user_tags.replace(char, "")

                            directory = f"media/{dt_now}_{safe_user_tags}"
                            os.makedirs(directory, exist_ok=True)

                            with open(f"{directory}/{str(image_id)}.{image_format[-1]}", 'wb') as handler:
                                handler.write(img_data)

                            if db != False:
                                with open("db/rule34.db", "a") as db_writer:
                                    db_writer.write(f"{str(image_id)}\n")

                            bar()

                    print(colored(f"Page {page} Completed", "green"))
                    approved_list.clear()
                    page += 1

            return {"status": "ok"}

        except Exception as e:
            return {"status": "error", "uinput": user_tags, "exception": str(e), "extra": raw_req.content}
