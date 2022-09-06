import os.path

from src.twitter_video_dl import twitter_video_dl as tvdl
from datetime import datetime


def twitter_dl(phone, link):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    dl_path = os.path.join(BASE_DIR, f'music/{phone}/')
    if not os.path.exists(dl_path):
        os.mkdir(dl_path)
    file_name = f"music/{phone}/{datetime.now().strftime('%Y%m%d%H%M%S')}.mp4"
    print(f"downloading video from twitter link: {link}")
    tvdl.download_video(link, file_name)
    return file_name
