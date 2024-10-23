import requests
import random
from termcolor import colored
from time import sleep
from alive_progress import alive_bar
import os
import json

from main import unsafe_chars
from main import version

class Luscious():
    def Fetcher(proxy_list, user_proxies, header, URL):
        try:
            # sort link for category
            parts = URL.split("/")
            if parts[3] == "pictures":
                title = parts[5].partition("_")
                id = parts[5].rpartition("_")
            elif parts[3] in ["album", "albums"]:
                title = parts[4].partition("_")
                id = parts[4].rpartition("_")
            else:
                print("An error occured! Please report this with the link you used.")
                sleep(5)
                return
            id = id[2]
            title = title[0]
            
            page = 1
            completed_items = 0
            while True:
                header = {"User-Agent":f"nn-downloader/{version} (by Official Husko on GitHub)", "Content-Type": "application/json", "Accept": "application/json"}
                data = {"id":"6","operationName":"PictureListInsideAlbum","query":"\n    query PictureListInsideAlbum($input: PictureListInput!) {\n  picture {\n    list(input: $input) {\n      info {\n        ...FacetCollectionInfo\n      }\n      items {\n        __typename\n        id\n        title\n        description\n        created\n        like_status\n        number_of_comments\n        number_of_favorites\n        moderation_status\n        width\n        height\n        resolution\n        aspect_ratio\n        url_to_original\n        url_to_video\n        is_animated\n        position\n        permissions\n        url\n        tags {\n          category\n          text\n          url\n        }\n        thumbnails {\n          width\n          height\n          size\n          url\n        }\n      }\n    }\n  }\n}\n    \n    fragment FacetCollectionInfo on FacetCollectionInfo {\n  page\n  has_next_page\n  has_previous_page\n  total_items\n  total_pages\n  items_per_page\n  url_complete\n}\n    ","variables":{"input":{"filters":[{"name":"album_id","value":id}],"display":"position","items_per_page":50,"page":page}}}
                data = json.dumps(data)
                API_URL = "https://members.luscious.net/graphql/nobatch/?operationName=PictureListInsideAlbum"
                if user_proxies == True:
                    proxy = random.choice(proxy_list)
                    raw_req = requests.post(API_URL, headers=header, proxies=proxy, data=data)
                else:
                    raw_req = requests.post(API_URL, headers=header, data=data)
                
                req = raw_req.json()

                avail_sites = req["data"]["picture"]["list"]["info"]["total_pages"]
                total_items = req["data"]["picture"]["list"]["info"]["total_items"]
                
                if page > avail_sites:
                    print("")
                    print(colored(f"No Further Sites Found.", "green"))
                    sleep(3)
                    break
                
                if req["data"]["picture"]["list"]["items"] == [] and page == 2:
                    print("An error occured! Please report this with the link you used.")
                    sleep(5)
                    break

                # Download Each file
                with alive_bar(total_items, calibrate=1, dual_line=True, title='Downloading') as bar:
                    for _ in range(completed_items):
                        bar()
                    for item in req["data"]["picture"]["list"]["items"]:
                        
                        image_id = item["id"]
                        image_title = item["title"]
                        image_address = item["url_to_original"]
                        image_format = image_address.rpartition(".")
                        bar.text = f'-> Downloading: {image_title}, please wait...'
                        
                        if user_proxies == True:
                            proxy = random.choice(proxy_list)
                            img_data = requests.get(image_address, proxies=proxy).content
                        else:
                            sleep(1)
                            img_data = requests.get(image_address).content

                        safe_title = title.replace(" ", "_")
                        for char in unsafe_chars:
                            safe_title = safe_title.replace(char, "")

                        safe_image_title = image_title.replace(" ", "_")
                        for char in unsafe_chars:
                            safe_image_title = safe_image_title.replace(char, "")

                        if not os.path.exists(f"media/{safe_title}"):
                            os.mkdir(f"media/{safe_title}")
                        with open(f"media/{safe_title}/{str(safe_image_title)}.{image_format[2]}", 'wb') as handler:
                            handler.write(img_data)
                        bar()
                        completed_items += 1

                print(colored(f"Page {page} Completed", "green"))
                page += 1
                sleep(5)

            return {"status": "ok"}

        except Exception as e:
            return {"status": "error", "uinput": URL, "exception": str(e), "extra": raw_req.content}
