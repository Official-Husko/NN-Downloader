import requests
import random
from termcolor import colored
from alive_progress import alive_bar
from time import sleep
from datetime import datetime
import os

now = datetime.now()
dt_now = now.strftime("%d-%m-%Y_%H-%M-%S")

class FURBOORU():
    def Fetcher(user_tags, user_blacklist, proxy_list, max_sites, user_proxies, apiKey, header):
        user_tags = user_tags.replace(" ", ", ")
        print(user_tags)
        approved_list = []
        page = 1
        while True:
            URL = f"https://furbooru.org/api/v1/json/search/images?q={user_tags}&page={page}&key={apiKey}&per_page=50"
            if user_proxies == True:
                proxy = random.choice(proxy_list)
                req = requests.get(URL, headers=header, proxies=proxy).json()
            else:
                req = requests.get(URL, headers=header).json()
            if req == []:
                break
            elif page == max_sites:
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
                        if passed == user_blacklist_lenght:
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
                        safe_user_tags = user_tags.replace("\\", "").replace("/", "").replace(":", "").replace("*", "").replace("?", "").replace('"', "").replace("<", "").replace(">", "").replace("|", "").replace(" ", "_")
                        if not os.path.exists("media/" + dt_now + " " + safe_user_tags):
                            os.mkdir("media/" + dt_now + " " + safe_user_tags)
                        with open("media/" + dt_now + " " + safe_user_tags + "/" + str(image_id) + "." + image_format, 'wb') as handler:
                            handler.write(img_data)
                        bar()
                print(colored(f"Page {page} Completed", "green"))
                approved_list.clear()
                page += 1