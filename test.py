from whatsappHandler import getAllowedChats
import db
import os
from time import sleep

from spotdl.command_line.core import Spotdl

from Bot import WaBot

bot = WaBot({"messages": ['1', '2']})


def promotion():
    chats = getAllowedChats()
    message = 'You can get self diagnosis easily. Just write ```disgnose``` then your condition.\n ' \
              'example:\n\n__diagnose ' \
              'I have a running nose__ '

    x = 0
    while x <= 6:
        bot.send_message("254790670635@c.us", f"{message}")
        x += 1
        sleep(4)


    m = "for lyrics, type 'lyrics then name of song'\nfor audio, type 'audio then name of song'"

    bot.send_message("254716218080@c.us", m)
    bot.send_message("254790670635@c.us", m)


def download(song, user):
    args = {
        "song": [song,],
        'output_file': 'music/' + user + '/{artist} - {track-name}.{output-ext}'
    }

    with Spotdl(args) as spotdl_handler:
        spotdl_handler.match_arguments()

    files = os.listdir(f'music/{user}')

    return f'music/{user}/{files[0]}'


print(download("The spectre ncs", 'steven'))
