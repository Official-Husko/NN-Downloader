from modules import E621, RULE34, ProxyScraper
import json
import os
from termcolor import colored
from ctypes import windll

os.system("cls")
version = "1.0.0"
windll.kernel32.SetConsoleTitleW("Husko's Steam Workshop Downloader | v" + version)
proxy_list = []

print(colored("======================================================================================================================", "red"))
print(colored("|                                                                                                                    |", "red"))
print(colored("|     " + colored("Product: ", "white") + colored("Husko's Steam Workshop Downloader", "green") + colored("                                                                     |", "red"), "red"))
print(colored("|     " + colored("Version: ", "white") + colored(version, "green") + colored("                                                                                                 |", "red"), "red"))
print(colored("|     " + colored("Description: ", "white") + colored("Download and Install SteamWorkshop mods with a few simple clicks.", "green") + colored("                                 |", "red"), "red"))
print(colored("|                                                                                                                    |", "red"))
print(colored("======================================================================================================================", "red"))
print("")

if os.path.exists("config.json"):
    with open("config.json") as cf:
        config = json.load(cf)
    user_blacklist = config["blacklisted_tags"]
    user_proxies = config["proxies"]

print(colored("What site do you want to download from?", "green"))
site = input(">> ").lower()
if site == "":
    site = "rule34"
print("")

print(colored("Please enter the tags you want to use", "green"))
user_tags = input(">> ").lower()
if user_tags == "":
    user_tags = ""
print("")

print(colored("How many pages would you like to get?", "green"), " (leave empty for max)")
max_sites = input(">> ").lower()
print("")

if user_proxies == True:
    print(colored("Fetching Fresh Proxies...", "yellow"))
    ProxyScraper.Scraper(proxy_list=proxy_list)
    print("")

if site == "e621":
    E621.Fetcher(user_tags=user_tags, user_blacklist=user_blacklist)
elif site == "rule34":
    RULE34.Fetcher(user_tags=user_tags, user_blacklist=user_blacklist, proxy_list=proxy_list, max_sites=max_sites, user_proxies=user_proxies)
else:
    print(colored("Site not supported", "red"))


print("finish print")