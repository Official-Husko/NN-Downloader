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

class FURBOORU():
    def Fetcher(user_tags, user_blacklist, proxy_list, max_sites, user_proxies, apiKey, header, db):
        try:
            user_tags = user_tags.replace(" ", ", ")
            approved_list = []
            page = 1
            while True:
                URL = f"https://furbooru.org/api/v1/json/search/images?q={user_tags}&page={page}&key={apiKey}&per_page=50"
                if user_proxies == True:
                    proxy = random.choice(proxy_list)
                    raw_req = requests.get(URL, headers=header, proxies=proxy)
                else:
                    raw_req = requests.get(URL, headers=header)

                req = raw_req.json()

                if req["total"] == 0:
                    print(colored("No images found or all downloaded! Try different tags.", "yellow"))
                    sleep(5)
                    break
                elif page == max_sites:
                    print(colored(f"Finished Downloading {max_sites} of {max_sites} pages.", "yellow"))
                    sleep(5)
                    break
                else: 
                    for item in req["images"]:
                        image_hidden = item["hidden_from_users"]
                        if image_hidden != False:
                            pass
                        else:
                            post_tags = item["tags"]
                            image_address = item["representations"]["full"]
                            image_format = item["format"]
                            image_id = item["id"]
                            user_blacklist_lenght = len(user_blacklist)
                            passed = 0

                            for blacklisted_tag in user_blacklist:
                                if blacklisted_tag in post_tags:
                                    break
                                else:
                                    passed += 1
                            if passed == user_blacklist_lenght and str(image_id) not in db:
                                image_data = {"image_address": image_address, "image_format": image_format, "image_id": image_id}
                                approved_list.append(image_data)
                            else:
                                pass
                    with alive_bar(len(approved_list), calibrate=1, dual_line=True, title='Downloading') as bar:
                        for data in approved_list:
                            image_address = data["image_address"]
                            image_format = data["image_format"]
                            image_id = data["image_id"]
                            bar.text = f'-> Downloading: {image_id}, please wait...'
                            if user_proxies == True:
                                proxy = random.choice(proxy_list)
                                img_data = requests.get(image_address, proxies=proxy).content
                            else:
                                sleep(1)
                                img_data = requests.get(image_address).content

                            safe_user_tags = user_tags.replace(" ", "_")
                            for char in unsafe_chars:
                                safe_user_tags = safe_user_tags.replace(char, "")

                            if not os.path.exists(f"media/{dt_now}_{safe_user_tags}"):
                                os.mkdir(f"media/{dt_now}_{safe_user_tags}")
                            with open(f"media/{dt_now}_{safe_user_tags}/{str(image_id)}.{image_format}", 'wb') as handler:
                                handler.write(img_data)
                            with open("db/furbooru.db", "a") as db_writer:
                                db_writer.write(f"{str(image_id)}\n")
                            bar()
                    print(colored(f"Page {page} Completed", "green"))
                    approved_list.clear()
                    page += 1

            return {"status": "ok"}
        
        except Exception as e:
            return {"status": "error", "uinput": user_tags, "exception": str(e), "extra": raw_req.content}