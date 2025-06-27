"""Async downloaders for NN-Downloader v2.0"""

from .multporn_async import MultpornDownloader, download_multporn_comic
from .rule34_async import Rule34Downloader, download_rule34_tags
from .luscious_async import LusciousDownloader, download_luscious_album
from .yiffer_async import YifferDownloader, download_yiffer_comic
from .e621_async import E621Downloader, download_e621_tags
from .furbooru_async import FurbooruDownloader, download_furbooru_tags

__all__ = [
    'MultpornDownloader', 'download_multporn_comic',
    'Rule34Downloader', 'download_rule34_tags', 
    'LusciousDownloader', 'download_luscious_album',
    'YifferDownloader', 'download_yiffer_comic',
    'E621Downloader', 'download_e621_tags',
    'FurbooruDownloader', 'download_furbooru_tags'
]