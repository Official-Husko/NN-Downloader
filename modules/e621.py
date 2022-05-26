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

class E621():
    def Fetcher(user_tags, user_blacklist, proxy_list, max_sites, user_proxies, apiUser ,apiKey, header):
        last_id = ""
        approved_list = []
        page = 1
        api_limit = ""
        while True:
            URL = f"https://e621.net/posts.json?tags={user_tags}&limit=750&page={last_id}"
            if user_proxies == True:
                proxy = random.choice(proxy_list)
                req = requests.get(URL, headers=header, proxies=proxy, auth=HTTPBasicAuth(apiUser, apiKey)).json()
            else:
                req = requests.get(URL, headers=header, auth=HTTPBasicAuth(apiUser, apiKey)).json()
            try: 
                api_limit = req["message"]
                print(colored(api_limit + " (API limit)", "red"))
            except:
                pass
            if api_limit == "You cannot go beyond page 750. Please narrow your search terms.":
                break
            elif page == max_sites:
                break
            else: 
                for item in req["posts"]:
                    """print(item)
                    sleep(3)"""
                    image_id = item["id"]
                    image_address = item["file"]["url"]
                    post_tags1 = item["tags"]["general"]
                    post_tags2 = item["tags"]["species"]
                    post_tags3 = item["tags"]["character"]
                    post_tags4 = item["tags"]["copyright"]
                    post_tags5 = item["tags"]["artist"]
                    post_tags = post_tags1 + post_tags2 + post_tags3 + post_tags4 + post_tags5
                    image_format = item["file"]["ext"]
                    """print(image_id)
                    print(image_address)
                    print(post_tags)
                    print(post_tags1)
                    print(post_tags2)
                    print(image_format)
                    print("")
                    sleep(3)"""
                    user_blacklist_lenght = len(user_blacklist)
                    #print("Bad: ", user_blacklist_lenght)
                    passed = 0

                    for blacklisted_tag in user_blacklist:
                        if blacklisted_tag in post_tags:
                            """print(blacklisted_tag)"""
                            break
                        else:
                            passed += 1
                    """print("Good: ", passed)"""
                    if passed == user_blacklist_lenght:
                        image_data = {"image_address": image_address, "image_format": image_format, "image_id": image_id}
                        approved_list.append(image_data)
                        """print(colored(f"{image_id} passed the test!", "green"))
                        print("")"""
                    else:
                        pass
                        """print(colored(f"{image_id} did not pass the test!", "red"))
                        print("")"""
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
                    if not os.path.exists("media/" + dt_now + " " + user_tags):
                        os.mkdir("media/" + dt_now + " " + user_tags)
                    with open("media/" + dt_now + " " + user_tags + "/" + str(image_id) + "." + image_format, 'wb') as handler:
                        handler.write(img_data)
                    bar()
            print(colored(f"Page {page} Completed", "green"))
            approved_list.clear()
            page += 1
            print(last_id)
            last_id = "a" + str(image_id)