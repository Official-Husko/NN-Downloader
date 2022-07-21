import requests
import random
from termcolor import colored
from time import sleep
from alive_progress import alive_bar
import os

class Luscious():
    def Fetcher(proxy_list, user_proxies, header, URL):

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
        while True:
            querystring = {"operationName":"AlbumListOwnPictures","query":"query AlbumListOwnPictures($input: PictureListInput!) { picture { list(input: $input) { info { ...FacetCollectionInfo } items { id title url_to_original url_to_video tags { text } } } } } fragment FacetCollectionInfo on FacetCollectionInfo { page has_next_page total_items total_pages items_per_page url_complete }","variables":"{\"input\":{\"filters\":[{\"name\":\"album_id\",\"value\":\"" + str(id) + "\"}],\"display\":\"rating_all_time\",\"page\":" + str(page) + "}}"}
            URL = "https://api.luscious.net/graphql/nobatch/"
            if user_proxies == True:
                proxy = random.choice(proxy_list)
                req = requests.get(URL, headers=header, proxies=proxy, params=querystring).json()
            else:
                req = requests.get(URL, headers=header, params=querystring).json()
            
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
                    if not os.path.exists(f"media/{title}"):
                        os.mkdir(f"media/{title}")
                    with open(f"media/{title}/{str(image_title)}.{image_format[2]}", 'wb') as handler:
                        handler.write(img_data)
                    bar()

            print(colored(f"Page {page} Completed", "green"))
            page += 1
            sleep(5)
