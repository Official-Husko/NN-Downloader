import requests
import random
import re
import xmltodict
from termcolor import colored
from time import sleep
from alive_progress import alive_bar
import os

from main import unsafe_chars

class Multporn():
    def Fetcher(proxy_list, user_proxies, header, URL):
        try:
            media = []
            progress = 0

            # sort link for category
            parts = URL.split("/")
            type = parts[3]
            title = parts[4]

            if type in ["comics", "hentai_manga", "gay_porn_comics", "gif", "humor"]:
                type = "field_com_pages"

            elif type in ["pictures", "hentai"]:
                type = "field_img"

            elif type == "rule_63":
                type = "field_rule_63_img"

            elif type == "games":
                type = "field_screenshots"

            elif type == "video":
                print("[ " + colored("i","blue") + " ] " + "Sorry but videos are currently not supported.")
                sleep(5)
                return

            else:
                print("[ " + colored("i","blue") + " ] " + "Sorry but this type is not recognized. Please open a ticket with the link.")
                sleep(5)
                return

            # fetch item id
            if user_proxies == True:
                proxy = random.choice(proxy_list)
                raw_req = requests.get(URL, headers=header, proxies=proxy)
            else:
                raw_req = requests.get(URL, headers=header)

            # extract item id
            try:
                if raw_req.headers.get("link", None) is not None:
                    raw_link = raw_req.headers.get("link")

                else:
                    pattern = r'<link\s+rel="shortlink"\s+href="([^"]+)"\s*/?>'
                    # Search for the pattern in the HTML content
                    match = re.search(pattern, raw_req.text)
                    
                    if match:
                        raw_link = match.group(1)

            except Exception as e:
                print("[ " + colored("-","red") + " ] " + f"Node Link not Found. Double check the link else report this. Error: {e}")
                sleep(5)
                return
                
            link = re.findall("(http|https|ftp):[/]{2}([a-zA-Z0-9-.]+.[a-zA-Z]{2,4})(:[0-9]+)?/?([a-zA-Z0-9-._?,'/\+&%$#=~]*)", raw_link)
            id = link[0][3]

            # fetch juicebox with all images inside
            FURL = f"https://multporn.net/juicebox/xml/field/node/{id}/{type}/full"
            if user_proxies == True:
                proxy = random.choice(proxy_list)
                req = requests.get(FURL, headers=header, proxies=proxy)
            else:
                req = requests.get(FURL, headers=header)
            
            # something really got fucked if it returns 404
            if req.status_code == 404:
                print(colored("An error occurred! please report this to the dev"))
                sleep(3)
                return

            # convert the xml to json for the sake of my mental health
            juicebox_data = xmltodict.parse(req.content)

            # get all images into a list
            for images in juicebox_data["juicebox"]["image"]:
                image_url = images["@linkURL"]
                media.append(image_url)
            
            # Download all images
            with alive_bar(len(media), calibrate=1, dual_line=True, title='Downloading') as bar:
                bar.text = f'-> Downloading: {title}, please wait...'
                for image in media:
                    image_format = image.rpartition(".")
                    progress += 1
                    if user_proxies == True:
                        proxy = random.choice(proxy_list)
                        img_data = requests.get(image, proxies=proxy).content
                    else:
                        sleep(1)
                        img_data = requests.get(image).content

                    safe_title = title.replace(" ", "_")
                    for char in unsafe_chars:
                        safe_title = safe_title.replace(char, "")

                    if not os.path.exists(f"media/{safe_title}"):
                        os.mkdir(f"media/{safe_title}")
                    with open(f"media/{safe_title}/{str(progress)}.{image_format[2]}", 'wb') as handler:
                        handler.write(img_data)
                    bar()
            print("[ " + colored("i","blue") + " ] " + f"Completed downloading {title}!")
            sleep(5)

            return {"status": "ok"}

        except Exception as e:
            return {"status": "error", "uinput": URL, "exception": str(e), "extra": raw_req.content}