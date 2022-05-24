import requests
from requests.auth import HTTPBasicAuth
import json

class E621():
    def Fetcher(user_tags):
        header = {"User-Agent":"nn-downloader/1.0 (by Official Husko)"}
        apiKey = ""
        apiUser = ""
        URL = f"https://e621.net/posts.json?tags={user_tags}&limit=750&page=b3308982"
        print(URL)
        req = requests.get(URL, headers=header, auth=HTTPBasicAuth(apiUser,apiKey))
        data = req.json()
        print(data)