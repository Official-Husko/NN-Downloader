from modules import *
import json
import os
from termcolor import colored
from ctypes import windll
from time import sleep
from sys import exit
import inquirer

version = "1.4.0"
windll.kernel32.SetConsoleTitleW(f"NN-Downloader | v{version}")
proxy_list = []
header = {"User-Agent":f"nn-downloader/{version} (by Official Husko on GitHub)"}
needed_folders = ["db", "media"]
database_list = ["e621.db"]

if os.path.exists("outdated"):
    version_for_logo = colored(f"v{version}", "cyan", attrs=["blink"])
else:
    version_for_logo = colored(f"v{version}", "cyan")

logo = f"""{colored(f'''
d8b   db d8b   db        d8888b.  .d88b.  db   d8b   db d8b   db db       .d88b.   .d8b.  d8888b. d88888b d8888b. 
888o  88 888o  88        88  `8D .8P  Y8. 88   I8I   88 888o  88 88      .8P  Y8. d8' `8b 88  `8D 88'     88  `8D 
88V8o 88 88V8o 88        88   88 88    88 88   I8I   88 88V8o 88 88      88    88 88ooo88 88   88 88ooooo 88oobY' 
88 V8o88 88 V8o88 C8888D 88   88 88    88 Y8   I8I   88 88 V8o88 88      88    88 88~~~88 88   88 88~~~~~ 88`8b   
88  V888 88  V888        88  .8D `8b  d8' `8b d8'8b d8' 88  V888 88booo. `8b  d8' 88   88 88  .8D 88.     88 `88. 
VP   V8P VP   V8P        Y8888D'  `Y88P'   `8b8' `8d8'  VP   V8P Y88888P  `Y88P'  YP   YP Y8888D' Y88888P 88   YD 
                                                                                        {version_for_logo} | by {colored("Official-Husko", "yellow")}''', "red")}
"""

class Main():
    def main_startup():
        os.system("cls")
        print(logo)
        print("")

        # Check if needed folders exists else create them
        for folder in needed_folders:
            if not os.path.exists(folder):
                os.mkdir(folder)

        
        if os.path.exists("config.json"):
            config = Config_Manager.reader()
            oneTimeDownload = config["oneTimeDownload"]
            use_proxies = config["proxies"]
            checkForUpdates = config["checkForUpdates"]
        else:
            config = Config_Manager.creator()
            print(colored("New Config file generated. Please configure it for your use case and add API keys for needed services.", "green"))
            sleep(7)
            exit(0)

        if checkForUpdates == True:
            os.system("cls")
            print(logo)
            print("")
            print(colored("Checking for Updates...", "yellow"), end='\r')
            AutoUpdate.Checker()
            os.system("cls")
            print(logo)
            print("")

        if use_proxies == True:
            print(colored("Fetching Fresh Proxies...", "yellow"), end='\r')
            ProxyScraper.Scraper(proxy_list=proxy_list)
            print(colored(f"Fetched {len(proxy_list)} Proxies.        ", "green"))
            print("")

        if oneTimeDownload == True:
            for database in database_list:
                with open(f"db/{database}", "a") as db_creator:
                    db_creator.close()

        print(colored("What site do you want to download from?", "green"))
        questions = [
            inquirer.List('selection',
                          choices=['E621', 'E926', 'Furbooru', 'Luscious', 'Multporn', 'Rule34', 'Yiffer']),
        ]
        answers = inquirer.prompt(questions)
        print("")

        site = answers.get("selection").lower()

        if site in ["multporn", "yiffer", "luscious"]:
            pass
        else: 
            print(colored("Please enter the tags you want to use", "green"))
            user_tags = input(">> ").lower()
            while user_tags == "":    
                print(colored("Please enter the tags you want.", "red"))
                sleep(3)
                user_tags = input(">> ").lower()
            print("")

            print(colored("How many pages would you like to get?", "green"), colored(" (leave empty for max)", "yellow"))
            max_sites = input(">> ").lower()
            print("")

        if site == "e621":
            apiUser = config["user_credentials"]["e621"]["apiUser"]
            apiKey = config["user_credentials"]["e621"]["apiKey"]
            if oneTimeDownload == True:
                with open("db/e621.db", "r") as db_reader:
                    database = db_reader.read().splitlines()
            if apiKey == "" or apiUser == "":
                print(colored("Please add your Api Key into the config.json", "red"))
                sleep(5)
            else:
                E621.Fetcher(user_tags=user_tags, user_blacklist=config["blacklisted_tags"], proxy_list=proxy_list, max_sites=max_sites, user_proxies=config["proxies"], apiUser=apiUser, apiKey=apiKey, header=header, db=database)
        elif site == "e926":
            apiUser = config["user_credentials"]["e926"]["apiUser"]
            apiKey = config["user_credentials"]["e926"]["apiKey"]
            if oneTimeDownload == True:
                with open("db/e621.db", "r") as db_reader:
                    database = db_reader.read().splitlines()
            if apiKey == "" or apiUser == "":
                print(colored("Please add your Api Key into the config.json", "red"))
                sleep(5)
            else:
                E926.Fetcher(user_tags=user_tags, user_blacklist=config["blacklisted_tags"], proxy_list=proxy_list, max_sites=max_sites, user_proxies=config["proxies"], apiUser=apiUser, apiKey=apiKey, header=header, db=database)
        elif site == "rule34":
            RULE34.Fetcher(user_tags=user_tags, user_blacklist=config["blacklisted_tags"], proxy_list=proxy_list, max_sites=max_sites, user_proxies=config["proxies"], header=header)
        elif site == "furbooru":
            apiKey = config["user_credentials"]["furbooru"]["apiKey"]
            if apiKey == "":
                print(colored("Please add your Api Key into the config.json", "red"))
                sleep(5)
            else:
                FURBOORU.Fetcher(user_tags=user_tags, user_blacklist=config["blacklisted_tags"], proxy_list=proxy_list, max_sites=max_sites, user_proxies=config["proxies"], apiKey=apiKey, header=header)
        elif site == "multporn":
            print(colored("Please enter the link. (e.g. https://multporn.net/comics/double_trouble_18)", "green"))
            URL = input(">> ")
            while URL == "":    
                print(colored("Please enter a valid link.", "red"))
                sleep(1.5)
                URL = input(">> ")
            Multporn.Fetcher(proxy_list=proxy_list, user_proxies=config["proxies"], header=header, URL=URL)
        elif site == "yiffer":
            print(colored("Please enter the link. (e.g. https://yiffer.xyz/Howl & Jasper)", "green"))
            URL = input(">> ")
            while URL == "":    
                print(colored("Please enter a valid link.", "red"))
                sleep(1.5)
                URL = input(">> ")
            Yiffer.Fetcher(proxy_list=proxy_list, user_proxies=config["proxies"], header=header, URL=URL)
        elif site == "luscious":
            print(colored("Please enter the link. (e.g. https://www.luscious.net/albums/bifurcation-ongoing_437722)", "green"))
            URL = input(">> ")
            while URL == "":    
                print(colored("Please enter a valid link.", "red"))
                sleep(1.5)
                URL = input(">> ")
            Luscious.Fetcher(proxy_list=proxy_list, user_proxies=config["proxies"], header=header, URL=URL)
        
        
        else:
            print(colored("Site not supported. Open a ticket to request support for that site!", "red"))

        # Jump back to start
        Main.main_startup()

if __name__ == '__main__':
    try:
        Main.main_startup()
    except KeyboardInterrupt:
        print("User Cancelled")
        sleep(3)
        exit(0)
        
        
"""
TODO: fix luscious being broken

"""