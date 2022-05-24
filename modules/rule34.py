import requests
import random
from termcolor import colored
from alive_progress import alive_bar
from time import sleep
from datetime import datetime
import os

now = datetime.now()
dt_now = now.strftime("%d-%m-%Y_%H-%M-%S")

class RULE34():
    def Fetcher(user_tags, user_blacklist, proxy_list, max_sites, user_proxies):
        approved_list = []
        page = 1
        header = {"User-Agent":"nn-downloader/1.0 (by Official Husko on GitHub)"}
        while True:
            URL = f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&pid={page}&limit=1000&json=1&tags={user_tags}"
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
                for item in req:
                    sleep(3)
                    #print(item)
                    post_tags = str.split(item["tags"])
                    image_address = item["file_url"]
                    image_name = item["image"]
                    image_id = item["id"]
                    user_blacklist_lenght = len(user_blacklist)
                    #print("Bad: ", user_blacklist_lenght)
                    passed = 0

                    for blacklisted_tag in user_blacklist:
                        if blacklisted_tag in post_tags:
                            #print(blacklisted_tag)
                            break
                        else:
                            passed += 1
                    #print("Good: ", passed)
                    if passed == user_blacklist_lenght:
                        image_data = {"image_address": image_address, "image_name": image_name, "image_id": image_id}
                        approved_list.append(image_data)
                        #print(colored(f"{image_id} passed the test!", "green"))
                        #print("")
                    else:
                        pass
                        #print(colored(f"{image_id} did not pass the test!", "red"))
                        #print("")
                with alive_bar(len(approved_list), calibrate=1) as bar:
                    for data in approved_list:
                        image_address = data["image_address"]
                        image_name = data["image_name"]
                        image_id = data["image_id"]
                        if user_proxies == True:
                            proxy = random.choice(proxy_list)
                            img_data = requests.get(image_address, proxies=proxy).content
                        else:
                            sleep(1)
                            img_data = requests.get(image_address).content
                        if not os.path.exists("media/" + dt_now + " " + user_tags):
                            os.mkdir("media/" + dt_now + " " + user_tags)
                        with open("media/" + dt_now + " " + user_tags + "/" + str(image_id) + " - " + image_name, 'wb') as handler:
                            handler.write(img_data)
                        bar()
                print(colored(f"Page {page} Completed", "green"))
                approved_list.clear()
                page += 1