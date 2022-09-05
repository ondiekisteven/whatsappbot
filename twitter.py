from src.twitter_video_dl import twitter_video_dl as tvdl
from datetime import datetime


def twitter_dl(phone, link):
    file_name = f"music/{phone}/{datetime.now().strftime('%Y%m%d%H%M%S')}.mp4"
    print(f"downloading video from twitter link: {link}")
    tvdl.download_video(link, file_name)
    return file_name
