from modules import *
import json
import os
from termcolor import colored
from time import sleep
import sys
import inquirer

version = "1.6.5"

if os.name == 'nt':
    from ctypes import windll
    windll.kernel32.SetConsoleTitleW(f"NN-Downloader | v{version}")

proxy_list = []
header = {"User-Agent":f"nn-downloader/{version} (by Official Husko on GitHub)"}
needed_folders = ["db", "media"]
database_list = ["e621", "e6ai", "e926", "furbooru", "rule34"]
unsafe_chars = ["/", "\\", ":", "*", "?", "\"", "<", ">", "|", "\0", "$", "#", "@", "&", "%", "!", "`", "^", "(", ")", "{", "}", "[", "]", "=", "+", "~", ",", ";", "~"]

if sys.gettrace() is not None:
    DEBUG = True
else:
    DEBUG = False

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
        def clear_screen():
            if os.name == 'nt':
                os.system("cls")
            else:
                os.system("clear")
        print(colored("Checking for read and write permissions.", "green"))

        # Check if the process has read and write permissions
        if os.access(os.getcwd(), os.R_OK | os.W_OK):
            pass
        else:
            print(colored("The program is missing read & write permissions! Change the directory or try run as administrator.", "red"))
            sleep(300)
            sys.exit(0)
        
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
            ai_training = config["ai_training"]
        else:
            config = Config_Manager.creator()
            print(colored("New Config file generated. Please configure it for your use case and add API keys for needed services.", "green"))
            sleep(7)
            sys.exit(0)

        if checkForUpdates == True:
            clear_screen()
            print(logo)
            print("")
            print(colored("Checking for Updates...", "yellow"), end='\r')
            AutoUpdate.Checker()
            clear_screen()
            print(logo)
            print("")

        if use_proxies == True:
            print(colored("Fetching Fresh Proxies...", "yellow"), end='\r')
            ProxyScraper.Scraper(proxy_list=proxy_list)
            print(colored(f"Fetched {len(proxy_list)} Proxies.        ", "green"))
            print("")

        if oneTimeDownload == True:
            for database in database_list:
                with open(f"db/{database}.db", "a") as db_creator:
                    db_creator.close()

        print(colored("What site do you want to download from?", "green"))
        questions = [
            inquirer.List('selection',
                          choices=['E621', 'E6AI', 'E926', 'Furbooru', 'Luscious', 'Multporn', 'Rule34', 'Yiffer']),
        ]
        answers = inquirer.prompt(questions)
        print("")

        site = answers.get("selection").lower()

        if site in ["e621", "e6ai", "e926", "furbooru", "rule34"]:

            print(colored("Please enter the tags you want to use.", "green"))
            user_tags = input(">> ").lower()

            # Check to make sure there are not more than 40 tags
            user_tags_split = user_tags.split()
            tags_count = len(user_tags_split)

            if site in ["e621", "e6ai", "e926"]:
                while user_tags == "" or tags_count > 40:
                    if user_tags == "":
                        print(colored("Please enter the tags you want.", "red"))
                    else:
                        print(colored(f"Sorry, {site.upper()} does not allow more than 40 tags.", "red"))
                        print(colored(f"You entered {tags_count} tags.", "red"))
                    
                    sleep(3)
                    user_tags = input(">> ").lower()

                    user_tags_split = user_tags.split()
                    tags_count = len(user_tags_split)
            else:
                while user_tags == "":    
                    print(colored("Please enter the tags you want.", "red"))
                    sleep(3)
                    user_tags = input(">> ").lower()


            print("")

            print(colored("How many pages would you like to get?", "green"), colored(" (leave empty for max)", "yellow"))
            max_sites = input(">> ").lower()
            print("")

        if site in ["e621", "e6ai", "e926"]:
            api_user = config.get("user_credentials",{}).get(site, {}).get("apiUser", "")
            api_key = config.get("user_credentials", {}).get(site, {}).get("apiKey", "")
            if oneTimeDownload == True:
                with open(f"db/{site}.db", "r") as db_reader:
                    database = db_reader.read().splitlines()
            else:
                database = False
            if api_key == "" or api_user == "":
                print(colored("Please add your API Key into the config.json", "red"))
                sleep(10)
                sys.exit(0)
            else:
                output = E6System.fetcher(user_tags=user_tags, user_blacklist=config["blacklisted_tags"], proxy_list=proxy_list, max_sites=max_sites, user_proxies=config["proxies"], api_user=api_user, api_key=api_key, header=header, db=database, site=site, ai_training=ai_training)
    
        elif site == "rule34":
            if oneTimeDownload == True:
                with open("db/rule34.db", "r") as db_reader:
                    database = db_reader.read().splitlines()
            else:
                database = False
            output = RULE34.fetcher(user_tags=user_tags, user_blacklist=config["blacklisted_tags"], proxy_list=proxy_list, max_sites=max_sites, user_proxies=config["proxies"], header=header, db=database)
        
        elif site == "furbooru":
            api_key = config.get("user_credentials", {}).get(site, {}).get("apiKey", "")
            if oneTimeDownload == True:
                with open("db/furbooru.db", "r") as db_reader:
                    database = db_reader.read().splitlines()
            else:
                database = False
            if api_key == "":
                print(colored("Please add your API Key into the config.json", "red"))
                sleep(5)
            else:
                output = FURBOORU.fetcher(user_tags=user_tags, user_blacklist=config["blacklisted_tags"], proxy_list=proxy_list, max_sites=max_sites, user_proxies=config["proxies"], api_key=api_key, header=header, db=database)
        
        elif site == "multporn":
            print(colored("Please enter the link. (e.g. https://multporn.net/comics/double_trouble_18)", "green"))
            URL = input(">> ")
            while URL == "":    
                print(colored("Please enter a valid link.", "red"))
                sleep(1.5)
                URL = input(">> ")
            output = Multporn.Fetcher(proxy_list=proxy_list, user_proxies=config["proxies"], header=header, URL=URL)
        
        elif site == "yiffer":
            print(colored("Please enter the link. (e.g. https://yiffer.xyz/Howl & Jasper)", "green"))
            URL = input(">> ")
            while URL == "":    
                print(colored("Please enter a valid link.", "red"))
                sleep(1.5)
                URL = input(">> ")
            output = Yiffer.Fetcher(proxy_list=proxy_list, user_proxies=config["proxies"], header=header, URL=URL)
        
        elif site == "luscious":
            print(colored("Please enter the link. (e.g. https://www.luscious.net/albums/bifurcation-ongoing_437722)", "green"))
            URL = input(">> ")
            while URL == "":    
                print(colored("Please enter a valid link.", "red"))
                sleep(1.5)
                URL = input(">> ")
            output = Luscious.Fetcher(proxy_list=proxy_list, user_proxies=config["proxies"], header=header, URL=URL)

        else:
            print(colored("Site not supported. Open a ticket to request support for that site!", "red"))
            raise Exception(f"This shouldn't be possible! User tried to download from {site}.")
            Main.main_startup()

        status = output.get("status", "why no status man?")
        uinput = output.get("uinput", "URL overdosed :(")
        exception_str = output.get("exception", "Fuck me there was no exception.")
        extra = output.get("extra", "")
        
        if status == "ok":
            pass
        
        elif status == "error":
            print(f"{error} An error occured while downloading from {colored(site, 'yellow')}! Please report this. Exception: {colored(exception_str, 'red')}")
            error_str = f"An error occured while downloading from {site}! Please report this. Exception: {exception_str}"
            Logger.log_event(error_str, extra, uinput)
            sleep(7)
        
        else:
            print(f"{major_error} An unknown error occured while downloading from {colored(site, 'yellow')}! Please report this. Exception: {colored(exception_str, 'red')}")
            error_str = f"An unknown error occured while downloading from {site}! Please report this. Exception: {exception_str}"
            Logger.log_event(error_str, extra, uinput)
            sleep(7)

        # Jump back to start
        Main.main_startup()

if __name__ == '__main__':
    try:
        Main.main_startup()
    except KeyboardInterrupt:
        print("User Cancelled")
        sleep(3)
        sys.exit(0)
