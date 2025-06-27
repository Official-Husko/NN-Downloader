import requests
import random
from termcolor import colored
from time import sleep
from alive_progress import alive_bar
import os

from main import unsafe_chars

class Yiffer():
    def Fetcher(proxy_list, user_proxies, header, URL):
        try:
            # link operations
            URL = requests.utils.unquote(URL, encoding='utf-8', errors='replace')
            parts = URL.split("/")
            title = parts[3]

            # Get item info
            URL = f"https://yiffer.xyz/api/comics/{title}"
            if user_proxies == True:
                proxy = random.choice(proxy_list)
                raw_req = requests.get(URL, headers=header, proxies=proxy)
            else:
                raw_req = requests.get(URL, headers=header)

            req = raw_req.json()

            pages = req["numberOfPages"]
            page_range = pages + 1

            # Download all images
            with alive_bar(pages, calibrate=1, dual_line=True, title='Downloading') as bar:
                bar.text = f'-> Downloading: {title}, please wait...'
                progress = 0
                for number in range(1,page_range):
                    progress += 1
                    if progress <= 9:
                        URL = f"https://static.yiffer.xyz/comics/{title}/00{progress}.jpg"
                    elif progress >= 10 and progress < 100:
                        URL = f"https://static.yiffer.xyz/comics/{title}/0{progress}.jpg"
                    else:
                        URL = f"https://static.yiffer.xyz/comics/{title}/{progress}.jpg"
                    if user_proxies == True:
                        proxy = random.choice(proxy_list)
                        img_data = requests.get(URL, proxies=proxy).content
                    else:
                        sleep(1)
                        img_data = requests.get(URL).content
                    
                    safe_title = title.replace(" ", "_")
                    for char in unsafe_chars:
                        safe_title = safe_title.replace(char, "")

                    if not os.path.exists(f"media/{safe_title}"):
                        os.mkdir(f"media/{safe_title}")
                    with open(f"media/{safe_title}/{str(number)}.jpg", "wb") as handler:
                        handler.write(img_data)
                    bar()
            print("[ " + colored("i","blue") + " ] " + f"Completed downloading {title}!")
            sleep(5)

            return {"status": "ok"}

        except Exception as e:
            return {"status": "error", "uinput": uinput, "exception": str(e), "extra": raw_req.content}