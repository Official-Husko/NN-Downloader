from modules import E621, RULE34, ProxyScraper, FURBOORU, E926, Multporn, Yiffer
import json
import os
from termcolor import colored
from ctypes import windll
from time import sleep
from sys import exit


version = "1.2.0"
windll.kernel32.SetConsoleTitleW(f"NN-Downloader | v{version}")
proxy_list = []
header = {"User-Agent":f"nn-downloader/{version} (by Official Husko on GitHub)"}

class Main():
    def main_startup():
        os.system("cls")
        print(colored("======================================================================================================================", "red"))
        print(colored("|                                                                                                                    |", "red"))
        print(colored("|     " + colored("Product: ", "white") + colored("NN-Downloader", "green") + colored("                                                                                         |", "red"), "red"))
        print(colored("|     " + colored("Version: ", "white") + colored(version, "green") + colored("                                                                                                 |", "red"), "red"))
        print(colored("|     " + colored("Description: ", "white") + colored("Download Naughty images fast from multiple sites.", "green") + colored("                                                 |", "red"), "red"))
        print(colored("|                                                                                                                    |", "red"))
        print(colored("======================================================================================================================", "red"))
        print("")

        # Check if media folder exists else create it
        if not os.path.exists("media"):
            os.mkdir("media")

        # Check if config exists else create it
        if os.path.exists("config.json"):
            with open("config.json") as cf:
                config = json.load(cf)
            user_blacklist = config["blacklisted_tags"]
            user_proxies = config["proxies"]
        else:
            default_config = {
                "proxies": "true",
                "user_credentials": {
                    "e621": {
                        "apiUser": "",
                        "apiKey": ""
                    },
                    "e926": {
                        "apiUser": "",
                        "apiKey": ""
                    },
                    "rule34": {
                        "user_id": "",
                        "pass_hash": "",
                        "comment": "currently not used"
                    },
                    "yiffer": {
                        "username": "",
                        "email": "",
                        "id": "",
                        "comment": "currently not used"
                    },
                    "yiffgallery": {
                        "pwg_id": "",
                        "comment": "currently not used"
                    },
                    "furbooru": {
                        "apiKey": ""
                    }
                },
                "blacklisted_tags": [
                    "example1",
                    "example2"
                ]
            }
            with open("config.json", "w") as cc:
                json.dump(default_config, cc, indent=6)
            cc.close()
            print(colored("New Config file generated. Please enter the Api Keys and the blacklisted tags in there after that restart the tool.", "green"))
            sleep(5)
            exit(0)

        if user_proxies == True:
            print(colored("Fetching Fresh Proxies...", "yellow"), end='\r')
            ProxyScraper.Scraper(proxy_list=proxy_list)
            print(colored(f"Fetched {len(proxy_list)} Proxies.        ", "green"))
            print("")

        print(colored("What site do you want to download from?", "green"))
        site = input(">> ").lower()
        if site == "":
            print(colored("Please enter a site.", "red"))
            sleep(3)
            Main.main_startup()
        print("")

        if site in ["multporn", "yiffer"]:
            pass
        else: 
            print(colored("Please enter the tags you want to use", "green"))
            user_tags = input(">> ").lower()
            if user_tags == "":
                print(colored("Please enter the tags you want.", "red"))
                sleep(3)
                Main.main_startup()
            print("")

            print(colored("How many pages would you like to get?", "green"), " (leave empty for max)")
            max_sites = input(">> ").lower()
            print("")

        if site == "e621":
            apiUser = config["user_credentials"]["e621"]["apiUser"]
            apiKey = config["user_credentials"]["e621"]["apiKey"]
            if apiKey == "" or apiUser == "":
                print(colored("Please add your Api Key into the config.json", "red"))
                sleep(3)
            else:
                E621.Fetcher(user_tags=user_tags, user_blacklist=user_blacklist, proxy_list=proxy_list, max_sites=max_sites, user_proxies=user_proxies, apiUser=apiUser, apiKey=apiKey, header=header)
        elif site == "e926":
            apiUser = config["user_credentials"]["e926"]["apiUser"]
            apiKey = config["user_credentials"]["e926"]["apiKey"]
            if apiKey == "" or apiUser == "":
                print(colored("Please add your Api Key into the config.json", "red"))
                sleep(3)
            else:
                E926.Fetcher(user_tags=user_tags, user_blacklist=user_blacklist, proxy_list=proxy_list, max_sites=max_sites, user_proxies=user_proxies, apiUser=apiUser, apiKey=apiKey, header=header)
        elif site == "rule34":
            RULE34.Fetcher(user_tags=user_tags, user_blacklist=user_blacklist, proxy_list=proxy_list, max_sites=max_sites, user_proxies=user_proxies, header=header)
        elif site == "furbooru":
            apiKey = config["user_credentials"]["furbooru"]["apiKey"]
            if apiKey == "":
                print(colored("Please add your Api Key into the config.json", "red"))
                sleep(3)
            else:
                FURBOORU.Fetcher(user_tags=user_tags, user_blacklist=user_blacklist, proxy_list=proxy_list, max_sites=max_sites, user_proxies=user_proxies, apiKey=apiKey, header=header)
        elif site == "multporn":
            print(colored("Please enter the link. (e.g. https://multporn.net/comics/double_trouble_18)", "green"))
            URL = input(">> ")
            Multporn.Fetcher(proxy_list=proxy_list, user_proxies=user_proxies, header=header, URL=URL)
        elif site == "yiffer":
            print(colored("Please enter the link. (e.g. https://yiffer.xyz/Howl & Jasper)", "green"))
            URL = input(">> ")
            Yiffer.Fetcher(proxy_list=proxy_list, user_proxies=user_proxies, header=header, URL=URL)


        else:
            print(colored("Site not supported. Open a ticket to request support for that site!", "red"))

        # Jump back to start
        Main.main_startup()

if __name__ == '__main__':
    Main.main_startup()