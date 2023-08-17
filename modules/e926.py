from requests.auth import HTTPBasicAuth
import requests
import random
from termcolor import colored
from alive_progress import alive_bar
from time import sleep
from datetime import datetime
import os

now = datetime.now()
dt_now = now.strftime("%d-%m-%Y_%H-%M-%S")

class E926():
    def Fetcher(user_tags, user_blacklist, proxy_list, max_sites, user_proxies, apiUser ,apiKey, header, db):
        approved_list = []
        page = 1
        while True:
            URL = f"https://e926.net/posts.json?tags={user_tags}&limit=320&page={page}"
            if user_proxies == True:
                proxy = random.choice(proxy_list)
                req = requests.get(URL, headers=header, proxies=proxy, auth=HTTPBasicAuth(apiUser, apiKey)).json()
            else:
                req = requests.get(URL, headers=header, auth=HTTPBasicAuth(apiUser, apiKey)).json()

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
                break
            
            else: 
                for item in req["posts"]:
                    image_id = item["id"]
                    image_address = item["file"]["url"]
                    post_tags1 = item["tags"]["general"]
                    post_tags2 = item["tags"]["species"]
                    post_tags3 = item["tags"]["character"]
                    post_tags4 = item["tags"]["copyright"]
                    post_tags5 = item["tags"]["artist"]
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
                        image_data = {"image_address": image_address, "image_format": image_format, "image_id": image_id}
                        approved_list.append(image_data)
                    else:
                        pass

            # Download Each file
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
                    with open("db/e621.db", "a") as db_writer:
                        db_writer.write(f"{str(image_id)}\n")
                    bar()

            print(colored(f"Page {page} Completed", "green"))
            approved_list.clear()
            page += 1
            sleep(5)