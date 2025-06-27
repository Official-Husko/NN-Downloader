import os
import json
import random
import requests
from requests.auth import HTTPBasicAuth
from termcolor import colored
from alive_progress import alive_bar
from time import sleep
from datetime import datetime

from main import unsafe_chars
from .create_directory import DirectoryManager

class E6System:
    @staticmethod
    def fetcher(user_tags, user_blacklist, proxy_list, max_sites, user_proxies, api_user, api_key, header, db, site, ai_training):
        try:
            Directory_Manager_Instance = DirectoryManager()

            approved_list = []
            now = datetime.now()
            dt_now = now.strftime("%d-%m-%Y_%H-%M-%S")
            page = 1
            
            while True:
                URL = f"https://{site}.net/posts.json?tags={user_tags}&limit=320&page={page}"
                proxy = random.choice(proxy_list) if user_proxies else None
                raw_req = requests.get(URL, headers=header, proxies=proxy, auth=HTTPBasicAuth(api_user, api_key))
                req = raw_req.json()
                
                if "message" in req and req["message"] == "You cannot go beyond page 750. Please narrow your search terms.":
                    print(colored(req["message"] + " (API limit)", "red"))
                    sleep(5)
                    break
                
                if not req["posts"]:
                    print(colored("No images found or all downloaded! Try different tags.", "yellow"))
                    sleep(5)
                    break
                
                elif page == max_sites:
                    print(colored(f"Finished Downloading {max_sites} of {max_sites} pages.", "yellow"))
                    sleep(5)
                    break
                
                else:
                    for item in req["posts"]:
                        image_id = item["id"]
                        image_address = item["file"].get("url")
                        meta_tags = item["tags"] if ai_training else []
                        post_tags = [item["tags"][tag_type] for tag_type in ["general", "species", "character"]]
                        post_tags += [item["tags"]["director"], item["tags"]["meta"]] if site == "e6ai" else [item["tags"]["copyright"], item["tags"]["artist"]]
                        post_tags = sum(post_tags, [])
                        user_blacklist_length = len(user_blacklist)

                        passed = sum(blacklisted_tag in post_tags for blacklisted_tag in user_blacklist)

                        if passed == 0 and not db and image_address and not any(tag in user_blacklist for tag in post_tags):
                            image_data = {"image_address": image_address, "image_format": item["file"]["ext"], "image_id": image_id, "meta_tags": meta_tags}
                            approved_list.append(image_data)

                        elif db and str(image_id) not in db and image_address and not any(tag in user_blacklist for tag in post_tags):
                            image_data = {"image_address": image_address, "image_format": item["file"]["ext"], "image_id": image_id, "meta_tags": meta_tags}
                            approved_list.append(image_data)

                with alive_bar(len(approved_list), calibrate=1, dual_line=True, title='Downloading') as bar:
                    for data in approved_list:
                        image_address = data.get("image_address")
                        image_format = data.get("image_format")
                        image_id = data.get("image_id")
                        meta_tags = data.get("meta_tags")
                        bar.text = f'-> Downloading: {image_id}, please wait...'

                        proxy = random.choice(proxy_list) if user_proxies else None
                        img_data = requests.get(image_address, proxies=proxy).content if user_proxies else requests.get(image_address).content

                        # TODO: Rewrite this because it currently does these static vars every time
                        directory = f"media/{dt_now} {user_tags}"

                        directory = Directory_Manager_Instance.create_folder(folder_name=directory)

                        meta_directory = f"{directory}/meta"

                        if ai_training == True:
                            os.makedirs(meta_directory, exist_ok=True)
                            with open(f"{meta_directory}/{str(image_id)}.json", 'w', encoding='utf-8') as handler:
                                json.dump(meta_tags, handler, indent=6)

                        with open(f"{directory}/{str(image_id)}.{image_format}", 'wb') as handler:
                            handler.write(img_data)

                        if db != False:
                            with open(f"db/{site}.db", "a", encoding="utf-8") as db_writer:
                                db_writer.write(f"{str(image_id)}\n")

                        bar()

                print(colored(f"Page {page} Completed", "green"))
                approved_list.clear()
                page += 1
                sleep(5)

            return {"status": "ok"}
        
        except Exception as e:
            return {"status": "error", "uinput": user_tags, "exception": str(e), "extra": raw_req.content}
