import requests
import random
import base64
from termcolor import colored
import inquirer
import webbrowser
import os
from time import sleep
from alive_progress import alive_bar

from main import version
from .logger import Logger
from .pretty_print import error, ok

class AutoUpdate:
    
    def Checker():
        try:
            url = "https://api.github.com/repos/Official-Husko/NN-Downloader/releases/latest?from=about"
            
            headers = {
                "User-Agent":f"nn-downloader/{version} (by Official Husko on GitHub)", 
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            }
            
            req = requests.get(url, headers=headers).json()
            repo_version = req.get("tag_name")
            download_link = req["assets"][0]["browser_download_url"]
            
            if str(version) < repo_version:
                print(colored("UPDATE AVAILABLE!      ", "red", attrs=["blink"]))
                
                body = req.get("body")
                name = req.get("name")
                date = req.get("published_at").replace("T", " ").replace("Z", "")
                
                print("")
                print(f"Latest release is {colored(name, 'light_blue')} released on {colored(date, 'yellow')}")
                print("")
                print(body)
                print("")
                amount_question = [
                inquirer.List('selection',
                                    message=colored("Do you want to download the update?", "green"),
                                    choices=["Yes", "No"],
                                    ),
                ]
                amount_answers = inquirer.prompt(amount_question)
                print("")
                decision = amount_answers.get("selection")
                if decision == "Yes":
                    r = requests.get(download_link, headers={"User-Agent":f"nn-downloader/{version} (by Official Husko on GitHub)"}, timeout=5, stream=True)
                    with alive_bar(int(int(r.headers.get('content-length')) / 1024 + 1)) as bar:
                        bar.text = f'-> Downloading Update {repo_version}, please wait...'
                        file = open(f"nn-downloader-{repo_version}.exe", 'wb')
                        for chunk in r.iter_content(chunk_size=1024):
                            if chunk:
                                file.write(chunk)
                                file.flush()
                                bar()
                    print(f"{ok} Update successfully downloaded! The program will now close and delete the old exe.")
                    if os.path.exists("delete-exe.bat"):
                        os.remove("delete-exe.bat")
                    with open("delete-exe.bat", "a") as bat_creator:
                        bat_content = f'TASKKILL -F /IM NN-Downloader.exe\ntimeout 3\nDEL .\\NN-Downloader.exe\nren .\\nn-downloader-{repo_version}.exe NN-Downloader.exe\nDEL .\\delete-exe.bat'
                        bat_creator.write(bat_content)
                        bat_creator.close()
                    os.startfile(r".\\delete-exe.bat")
                    sleep(5)
                    exit(0)
                elif decision == "No":
                    if not os.path.exists("outdated"):
                        with open("outdated", "a") as mark_outdated:
                            mark_outdated.close()
            elif str(version) >= repo_version:
                try:
                    os.remove("outdated")
                except Exception:
                    pass
        
        except Exception as e:
            # Construct and print the error
            error_str = f"An error occured while checking for updates! Please report this. Exception: {e}"
            print(f"{error} {error_str}")
            Logger.log_event(error_str, req)
            sleep(7)