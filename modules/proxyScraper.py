import requests

proxy_source_list = [
    "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
    "https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt",
    "https://raw.githubusercontent.com/Volodichev/proxy-list/main/http.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/roma8ok/proxy-list/main/proxy-list-http.txt"
]

# scrape proxies from a given destination
class ProxyScraper():
    def Scraper(proxy_list):
        for source in proxy_source_list:
            response = requests.get(source,headers={"User-Agent":"nn-downloader/1.0 (by Official Husko on GitHub)"},timeout=10)
            proxy_raw = response.text
            split_proxies = proxy_raw.split()
            for proxy in split_proxies:
                if proxy in proxy_list:
                    break
                else:
                    proxyy = {"http": proxy}
                    proxy_list.append(proxyy)
        return proxy_list