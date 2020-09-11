from whatsappHandler import getAllowedChats
import db
import os
from time import sleep

from spotdl.command_line.core import Spotdl

from Bot import WaBot


bot = WaBot({"messages": ['1', '2']})


def promotion():
    chats = getAllowedChats()
    print(chats)


def download(song, user):
    args = {
        "song": [song,],
        'output_file': 'music/' + user + '/{artist} - {track-name}.{output-ext}'
    }

    with Spotdl(args) as spotdl_handler:
        spotdl_handler.match_arguments()

    files = os.listdir(f'music/{user}')

    return f'music/{user}/{files[0]}'


promotion()
