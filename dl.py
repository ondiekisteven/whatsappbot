from audio import S3Uploader
from moviepy.editor import *
import os
import db
from json import dumps, loads

from youtube_dl import YoutubeDL
from youtube_search import YoutubeSearch


class MySearch(YoutubeSearch):
    """
    class which makes a youtube search for a song, saves the search results to a file and gives a printable result
    :param sid: chat_id of user who is downloading the song
    :param search_terms: the keywords of the song being searched
    """
    def __init__(self, search_terms: str, sid):
        super().__init__(search_terms, max_results=10)
        self.sid = sid

    def save_to_file(self, json_result):
        """
        This function saves the search results to a file. contents are a dictionary in string
        """
        db.save_link(f'{self.sid}', json_result)

    def get_printable(self):
        """
        this function saves search results to file, and also gives printable result to send to whatsapp
        :return: a string containing the song titles from the search
        """
        dict_result = self.to_dict()
        result = ''
        for index, item in enumerate(dict_result):
            result += f'{index + 1}. - _{item["title"]}_\n\n'
        self.save_to_file(dumps(dict_result))
        return result


class YtSearch:
    def __init__(self, choice: dict):
        self.choice = choice
        self.vid = self.choice['id']
        self.thumbnails = self.choice['thumbnails']
        self.title = self.choice['title']
        self.url = self.choice['url_suffix']

    def __str__(self):
        return self.title

    def get_url(self):
        return f"https://youtube.com{self.url}"


class DlSelector:
    def __init__(self, sid, choice: int):
        self.sid = sid
        self.choice = choice
        self.user_directory = f'music/{self.sid}'
        self.URLS_FILE = os.path.join(self.user_directory, 'YOUTUBE_LINKS.txt')

    def read_urls(self):
        # file = open(self.URLS_FILE)
        contents = db.get_link_text(self.sid)
        return contents

    def get_choice_url(self):
        contents = loads(self.read_urls())
        selected = YtSearch(contents[self.choice-1])
        return selected.get_url()


class Downloader(DlSelector):
    def __init__(self, sid, choice: int):
        super().__init__(sid, choice)
        self.url = self.get_choice_url()

    def download_audio(self):
        outtmpl = '/tmp/music/%(title)s' + '.%(ext)s'
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': outtmpl,
            'postprocessors': [
                {'key': 'FFmpegExtractAudio', 'preferredcodec': 'aac',
                 'preferredquality': '192',
                 },
                {'key': 'FFmpegMetadata'},
            ],
        }

        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(self.url, download=True)
        return info_dict["title"] + ".aac"


class Converter:
    def __init__(self, video_path):
        self.file_path = video_path
        self.audio_path = self.get_audio_path()

    def get_audio_path(self):
        return " ".join(self.file_path.split('.')[:-1]) + '.mp3'

    def convert(self):
        a_c = AudioFileClip(self.file_path)
        a_c.write_audiofile(self.audio_path)
        return os.path.basename(self.audio_path)


def download_song(song_url):
    """
    Download a song using youtube url and song title
    """

    outtmpl = '/tmp/music/%(title)s' + '.%(ext)s'
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': outtmpl,
        'postprocessors': [
            {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3',
             'preferredquality': '192',
             },
            {'key': 'FFmpegMetadata'},
        ],
    }

    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(song_url, download=True)
    return info_dict["title"] + ".mp3"


def save_to_s3(file_name):
    file_path = f'/tmp/music/{file_name}'
    uploader = S3Uploader()
    uploader.upload_file(file_path, f'music/{file_name}')
    return f'https://som-whatsapp.s3.us-east-2.amazonaws.com/music/{file_name}'
