import requests
import random
import re
import json
import xmltodict
from termcolor import colored
from time import sleep
from alive_progress import alive_bar
import os

class Multporn():
    def Fetcher(proxy_list, user_proxies, header, URL):

        media = []
        progress = 0

        # sort link for category
        parts = URL.split("/")
        title = parts[4]

        if parts[3] == "comics":
            type = "field_com_pages"

        if parts[3] == "hentai_manga":
            type = "field_com_pages"

        elif parts[3] == "pictures":
            type = "field_img"

        elif parts[3] == "rule_63":
            type = "field_rule_63_img"

        elif parts[3] == "gay_porn_comics":
            type = "field_com_pages"

        elif parts[3] == "hentai":
            type = "field_img"

        elif parts[3] == "games":
            type = "field_screenshots"

        elif parts[3] == "video":
            print("[ " + colored("i","blue") + " ] " + "Sorry but videos are currently not supported.")
            sleep(5)
            return

        elif parts[3].lower() == "gif":
            type = "field_com_pages"

        elif parts[3] == "humor":
            type = "field_com_pages"

        else:
            print("[ " + colored("i","blue") + " ] " + "Sorry but this type is not recognized. Please open a ticket with the link.")
            sleep(5)
            return

        # fetch item id
        if user_proxies == True:
            proxy = random.choice(proxy_list)
            req = requests.get(URL, headers=header, proxies=proxy).headers
        else:
            req = requests.get(URL, headers=header).headers

        # extract item id
        try:
            raw_link = req["link"]
        except:
            print("[ " + colored("-","red") + " ] " + f"Please provide a correct link! If this is a mistake please open a ticked with the url.")
            sleep(5)
            return
            
        link = re.findall("(http|https|ftp):[/]{2}([a-zA-Z0-9-.]+.[a-zA-Z]{2,4})(:[0-9]+)?/?([a-zA-Z0-9-._?,'/\+&%$#=~]*)", raw_link)
        id = link[0][3]

        # fetch juicebox with all images inside
        URL = f"https://multporn.net/juicebox/xml/field/node/{id}/{type}/full"
        if user_proxies == True:
            proxy = random.choice(proxy_list)
            req = requests.get(URL, headers=header, proxies=proxy)
        else:
            req = requests.get(URL, headers=header)
        
        # something really got fucked if it returns 404
        if req.status_code == 404:
            print(colored("An error occurred! please report this to the dev"))
            sleep(3)
            pass

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
                if not os.path.exists(f"media/{title}"):
                    os.mkdir(f"media/{title}")
                with open(f"media/{title}/{str(progress)}.{image_format[2]}", "wb") as handler:
                    handler.write(img_data)
                bar()
        print("[ " + colored("i","blue") + " ] " + f"Completed downloading {title}!")
        sleep(5)
