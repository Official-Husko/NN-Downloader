from requests.auth import HTTPBasicAuth
import requests
import random
from termcolor import colored
from alive_progress import alive_bar
from time import sleep
from datetime import datetime
import os
import json

from main import unsafe_chars
now = datetime.now()
dt_now = now.strftime("%d-%m-%Y_%H-%M-%S")

class E6System():
    def Fetcher(user_tags, user_blacklist, proxy_list, max_sites, user_proxies, apiUser ,apiKey, header, db, site, ai_training):
        try:
            approved_list = []
            page = 1
            while True:
                URL = f"https://{site}.net/posts.json?tags={user_tags}&limit=320&page={page}"
                if user_proxies == True:
                    proxy = random.choice(proxy_list)
                    raw_req = requests.get(URL, headers=header, proxies=proxy, auth=HTTPBasicAuth(apiUser, apiKey))
                else:
                    raw_req = requests.get(URL, headers=header, auth=HTTPBasicAuth(apiUser, apiKey))

                req = raw_req.json()

                try:
                    if req["message"] == "You cannot go beyond page 750. Please narrow your search terms.": 
                        print(colored(req["message"] + " (API limit)", "red"))
                        sleep(5)
                        break
                except:
                    pass
                
                if req["posts"] == []:
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
                        image_address = item["file"]["url"]
                        post_tags1 = item["tags"]["general"]
                        post_tags2 = item["tags"]["species"]
                        post_tags3 = item["tags"]["character"]
                        if site == "e6ai":
                            post_tags4 = item["tags"]["director"]
                            post_tags5 = item["tags"]["meta"]
                        else:
                            post_tags4 = item["tags"]["copyright"]
                            post_tags5 = item["tags"]["artist"]
                        
                        if ai_training == True:
                            meta_tags = item["tags"]

                        post_tags = post_tags1 + post_tags2 + post_tags3 + post_tags4 + post_tags5
                        image_format = item["file"]["ext"]
                        user_blacklist_lenght = len(user_blacklist)
                        passed = 0

                        for blacklisted_tag in user_blacklist:
                            if blacklisted_tag in post_tags:
                                break
                            else:
                                passed += 1
                        if passed == user_blacklist_lenght and str(image_id) not in db and image_address != None:
                            image_data = {"image_address": image_address, "image_format": image_format, "image_id": image_id, "meta_tags": meta_tags}
                            approved_list.append(image_data)
                        else:
                            pass

                # Download Each file
                with alive_bar(len(approved_list), calibrate=1, dual_line=True, title='Downloading') as bar:
                    for data in approved_list:
                        image_address = data["image_address"]
                        image_format = data["image_format"]
                        image_id = data["image_id"]
                        meta_tags = data["meta_tags"]
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
                        if not os.path.exists(f"media/{dt_now}_{safe_user_tags}/meta") and ai_training == True:
                            os.mkdir(f"media/{dt_now}_{safe_user_tags}/meta")
                        with open(f"media/{dt_now}_{safe_user_tags}/{str(image_id)}.{image_format}", 'wb') as handler:
                            handler.write(img_data)
                        with open(f"media/{dt_now}_{safe_user_tags}/meta/{str(image_id)}.json", 'w') as handler:
                            json.dump(meta_tags, handler, indent=6)
                        with open(f"db/{site}.db", "a") as db_writer:
                            db_writer.write(f"{str(image_id)}\n")
                        bar()

                print(colored(f"Page {page} Completed", "green"))
                approved_list.clear()
                page += 1
                sleep(5)

            return {"status": "ok"}
        
        except Exception as e:
            return {"status": "error", "uinput": user_tags, "exception": str(e), "extra": raw_req.content}