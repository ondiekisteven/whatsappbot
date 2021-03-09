import requests
from json import dumps, loads

import wikipedia
from wikipedia import PageError, DisambiguationError

from dl import *
from pymysql import IntegrityError
from genius import Genius
from whatsappHandler import register, remove_first_word, is_group
import uuid
import os
import db
import random
from wiki import page, search_howto, search_howto_index, random_how_to
from spotdl.command_line.core import Spotdl
from dict import meaningSynonym, transFr, find_links, ACCEPTED_LINKS, get_languages_as_text, languages_list, \
    language_code, get_tld

adverts = [
    'Audio downloads are not stable yet, Dont download many songs in a short time, it will crash the bot',
    'Remember whatsapp has a size limit. Therefore, dont download dj mixes and other big files, They wont be sent here',
    'The bot downloads songs from  youtube. If we didnt find your song, its probably not in youtube yet',
    'If you dont receive your song quickly, send the command *join bot* to refresh the bot. It will send your song',
    'The bot is under testing, some features may not work perfect, be patient with them',
    'If you want to join in developing the bot, contact here: 0790670635',
]
os.environ["API_URL"] = 'https://api.chat-api.com/instance236876/'
os.environ["API_TOKEN"] = 'ry73iv1a9delxbwu'
os.environ["HEROKU_URL"] = 'http://localhost:5000/'
heroku_url = os.getenv('HEROKU_URL')
api_url = os.getenv('API_URL')
api_token = os.getenv('API_TOKEN')


def get_phone(message):
    return message['author'].replace('@c.us', '')


def sim(message: str):
    phone = message.split(' ')[0]
    arg = remove_first_word(message)
    body = {
        "messages": [
            {
                "body": arg,
                "fromMe": False,
                "author": f"254{phone[1:]}@c.us",
                "chatId": f"254{phone[1:]}@c.us", 
                "chatName": f"254{phone[1:]}"
            }
        ]
    }
    
    bot = WaBot(body)
    return bot.processing()


def delete_diagnosis_user(message):
    print('Removing user data from database...')
    phone = message['author'].replace('@c.us', '')
    db.deleteUserOngoingDiagnosis(phone)
    db.deleteUserSymptoms(phone)
    db.deleteUserCurrentSymptom(phone)
    db.deleteCurrentQuestion(phone)


def send_ppt(chat_id, audio):
    data = {
        "chatId": chat_id,
        "audio": audio
    }
    answer = requests.post('https://eu156.chat-api.com/instance176241/sendPTT?token=18tge8h634rmjh5t', data=data)

    return answer


def parse_phone(phone):
    # phone = '+254790670635'
    if phone.startswith('+'):
        phone = phone[1:]
    elif phone.startswith('0'):
        phone = f'254{phone[1:]}'
    print(f'Adding user {phone.replace(" ", "")}@c.us')
    return f'{phone.replace(" ", "")}@c.us'


class WaBot:

    def __init__(self, json):
        self.message = json
        self.APIUrl = api_url
        self.token = api_token
        self.last_command = "last command"

    def send_requests(self, method, data):
        url = f'{self.APIUrl}{method}?token={self.token}'
        headers = {'content-type': 'application/json'}
        answer = requests.post(url, data=dumps(data), headers=headers)
        y = answer.text
        return y

    def send_message(self, chat_id, text):
        data = {
            'chatId': chat_id,
            'body': text
        }
        answer = self.send_requests('sendMessage', data)
        return answer

    def send_file(self, chat_id, body, file_name, caption):

        data = {
            'chatId': chat_id,
            'body': body,
            'filename': file_name,
            'caption': caption
        }
        answer = self.send_requests('sendFile', data)
        return answer

    def get_song(self, path):
        contents = os.listdir(path)
        if contents:
            for c in contents:
                if c.endswith('.mp3'):
                    # print(f'Found one song: -> {c}')
                    # path = f'https://som-whatsapp.herokuapp.com/files/music/{get_phone(self.message)}/{c}'
                    return c  # self.send_file(self.message['chatId'], path, 'audio.mp3', 'audio')

        else:
            return "empty directory"

    def get_last_command(self):
        pass

    def download_audio(self, song, user):
        path = f'music/{user}/'

        args = {
            "song": [song],
            'output_file': f'music/{user}/' + '{artist} - {track-name}.{output-ext}'
        }
        print(f'Downloading to {path}')
        with Spotdl(args) as spotdl_handler:
            spotdl_handler.match_arguments()

        return path

    def welcome(self, chat_id, name):
        welcome_string = """
Hello, Here are the serivces i can offer you...

1. *Lyrics*   - Get lyrics of song 
e.g. *lyrics work - rihanna*


2. *audio*    - Get audio of a song.
e.g. *audio alan walker faded* or
*audio http//youtube.com...* (youtube link)

3. *wiki* - search wikipedia for a given topic
eg. _wiki coronavirus_

4. *how to ...* - how to do something
eg _how to bake a cake_


6. *define* - get definition of a term. It has to be just one word.
eg. define gallery

7. *Group* -Create a group using the bot. it adds the bot as a user
eg. group My Music Group

8. *adduser* - Add a user to a group. For this to work, make me an admin in the group.

*Commands* or *help* -Display this menu
    """

        text = f'{name} \n{welcome_string}'
        self.send_message(chat_id, text)
        return self.send_message(chat_id, 'use the examples given in each command to understand how it works')

    def genius_lyrics(self, chat_id, search, phone, download=False, ):
        try:
            bot = Genius()
            sid = bot.search_song(search)
            if 'Could not find' in sid:
                return 'Could not find song'
            song_id = sid['song_id']
            lyrics = bot.retrieve_lyrics(song_id)
            thumbnail = sid['song_thumbnail']
            name = sid['song_title']
            self.send_file(chat_id, thumbnail, uuid.uuid4().hex + '.jpg', name)
            text = f'TITLE: {name}\n\n{lyrics}'
        except IndexError:
            text = "Could not find lyrics"

        message_send = self.send_message(chat_id, text)

        return message_send

    def lyrics(self, chat_id, search):
        pass
        # lyrics = search_lyrics(search)
        # return self.send_message(chat_id, lyrics)

    def diagnose(self, author, chat_id, response):
        phone = author.replace('@c.us', '')
        reply = register(phone, response)
        self.send_message(chat_id, reply)
        return reply

    def group(self, author, name='My awesome group'):
        phone = author.replace('@c.us', '')
        data = {
            "groupName": name,
            "phones": phone,
            'messageText': 'Welcome to your new group. send the command join bot to activate the bot here.'
        }
        answer = self.send_requests('group', data)
        return answer

    def add_participant(self, group_id, participant_phone=None, participant_id=None, ):
        data = {
            'groupId': group_id
        }
        if participant_phone:
            phone_to_add = parse_phone(participant_phone)
            data['participantPhone'] = phone_to_add
        elif participant_id:
            data['participantChatId'] = participant_id
        else:
            return self.send_message(group_id, 'Missing user to add. use this format: adduser 07... ')
        ans = self.send_requests('addGroupParticipant', data)
        ans = loads(ans)
        
        return self.send_message(group_id, ans['message'])
    
    def remove_participant(self, group_id, participant_phone=None, participant_id=None, ):
        data = {
            'groupId': group_id
        }
        if participant_phone:
            phone_to_add = parse_phone(participant_phone)
            data['participantPhone'] = phone_to_add
        elif participant_id:
            data['participantChatId'] = participant_id
        else:
            return 'Missing user to remove'
        ans = self.send_requests('removeGroupParticipant', data)
        ans = loads(ans)
        
        return self.send_message(group_id, ans['message'] + "\nReason: Sending message with links")

    def processing(self):

        message = self.message
        text = message['body']

        sid = message['chatId']
        name = message['author']
        links = find_links(text)
        if not os.path.exists(f'music/{get_phone(message)}'):
            os.mkdir(f'music/{get_phone(message)}')
        if links:
            for link in links:
                if get_tld(link) in ['https://youtu.be/', 'https://www.youtube.com/', 'youtu.be', 'www.youtube.com']:
                    self.send_message(sid, 'Checking youtube link...')
                    song_title = YoutubeDL().extract_info(link, download=False)['title']
                    self.send_message(sid, f'Detected song: *{song_title}*\n\nDownloading song...')
                    audio_name = download_song(link, f'music/{get_phone(message)}')
                    path = f'{heroku_url}files/music/{get_phone(message)}/{audio_name}'
                    folder = f'music/{get_phone(message)}'
                    if os.path.exists(f'music/{get_phone(message)}/{audio_name}'):
                        print(f"Song found in {folder}/{audio_name}")
                        audio_sending = self.send_file(sid, path, "audio.mp3", "audio")
                        print(f'sending audio -> {audio_sending}')
                        for file in os.listdir(folder):
                            file_path = os.path.join(folder, file)
                            os.unlink(file_path)
                        db.delete_downloading(sid)
                        db.updateLastCommand(sid, 'audio')
                        selected_adv = random.choice(adverts)
                        txt = f'You song has downloaded.\n\n[*Note] {selected_adv}'
                        return self.send_message(sid, txt)
                    break
            return 'probably no youtube link'
        if text.lower().startswith('command') or text.lower().startswith('help'):
            db.updateLastCommand(sid, 'help')
            return self.welcome(sid, name)
        elif text.lower().startswith('sim'):
            message = remove_first_word(text)
            return sim(message)
        elif text.lower().startswith('transl'):
            return ''
            # try:
            #     db.add_translating(get_phone(message))
            # except IntegrityError:
            #     pass
            # term = remove_first_word(text)
            # if term:
            #     # user has defined sentence to be translated...
            #     db.updateLastCommand(sid, 'translation-language')
            #     db.update_translating(get_phone(message), term)
            #     return self.send_message(sid, f"Select the language to translate to\n\n{get_languages_as_text(languages_list)}")
            # else:
            #     # user has not defined sentence to be translated...
            #     db.updateLastCommand(sid, 'translation-text')
            #     return self.send_message(sid, 'Enter the word or sentence you want to translate')
        elif text.lower().startswith('def'):
            term = remove_first_word(text)
            meaning = meaningSynonym(term)
            return self.send_message(sid, meaning)
        elif text.lower().startswith('wiki'):
            search = remove_first_word(text)
            self.send_message(sid, f"Searching for {search}...")
            try:
                res = page(search)
                return self.send_message(sid, f'*{res["t"]}* \n\n{res["d"]}')
            except PageError:
                return self.send_message(sid, f"The page you searched  wasn't found.")
            except DisambiguationError as e:
                print(e)
                return self.send_message(sid, f"ERROR: {e}")
        elif text.lower().startswith('how to'):
            if text.lower().replace('how to', '').strip():
                db.updateLastCommand(sid, 'choice how-to')
                self.send_message(sid, 'Searching, please wait...')
                hts = search_howto(text.lower())
                db.add_how_to_search(sid, text.lower(), hts['size'])
                return self.send_message(sid, hts['articles'])
            else:
                self.send_message(sid, 'You did not specify what to search. Searching for random how-to item')
                db.updateLastCommand(sid, 'join bot')
                rht = random_how_to()
                return self.send_message(sid, rht)
        elif text.lower().startswith('audio'):
            search = remove_first_word(text)
            if not search:
                return self.send_message(sid,
                                         'To download audio, write audio then the name of the song or audio then a '
                                         'youtube link.')
            db.updateLastCommand(sid, 'audio')
            links = find_links(search)
            if links:
                self.send_message(sid, 'Checking link...')
                for link in links:
                    if get_tld(link) in ['https://youtu.be/', 'https://www.youtube.com/', 'youtu.be', 'www.youtube.com']:
                        song_title = YoutubeDL().extract_info(link, download=False)['title']
                        self.send_message(sid, f'Detected song: *{song_title}*\n\nDownloading song...')
                        audio_name = download_song(link, f'music/{get_phone(message)}')
                        path = f'{heroku_url}files/music/{get_phone(message)}/{audio_name}'
                        folder = f'music/{get_phone(message)}'
                        if os.path.exists(f'music/{get_phone(message)}/{audio_name}'):
                            print(f"Song found in {folder}/{audio_name}")
                            audio_sending = self.send_file(sid, path, "audio.mp3", "audio")
                            print(f'sending audio -> {audio_sending}')
                            for file in os.listdir(folder):
                                file_path = os.path.join(folder, file)
                                if file_path.startswith('YOUTUBE_LINKS'):
                                    continue
                                # os.unlink(file_path)
                            db.delete_downloading(sid)
                            db.updateLastCommand(sid, 'audio')
                            selected_adv = random.choice(adverts)
                            txt = f'You song has downloaded.\n\n[*Note] {selected_adv}'
                            return self.send_message(sid, txt)
                        break
                return 'probably no youtube link'
            else:
                ytsearch = MySearch(search, get_phone(message)).get_printable()
                return self.send_message(sid, ytsearch)

        elif text.lower().startswith('dl'):
            search = remove_first_word(text)
            if not search:
                return self.send_message(sid, 'To download audio, write audio then the name of the song or audio then '
                                              'a youtube link.')
            # return self.send_message(sid, 'audios are not working for now, type help to get other services')
            path = f'music/{get_phone(message)}/'
            if not os.path.exists(path):
                os.mkdir(path)
            if db.is_downloading(sid):
                try:
                    files = self.get_song(path)
                    if files == 'empty directory':
                        db.delete_downloading(sid)
                    else:
                        db.delete_downloading(sid)
                        return self.send_message(sid, 'Another song is downloading. Try again after 20 seconds. ')
                except FileNotFoundError:
                    os.mkdir(path)
            self.send_message(sid, "Downloading your song... please wait")
            db.add_downloading_user(sid)

            path = self.download_audio(search, get_phone(message))
            song = self.get_song(path)

            if song == 'empty directory':
                db.delete_downloading(sid)
                return self.send_message(sid, 'Error downloading song. Try downloading using this -> +254771816217\n\n')

            path = f'{heroku_url}files/music/{get_phone(message)}/{song}'
            if os.path.exists(f'music/{get_phone(message)}/{song}'):
                audio_sending = self.send_file(sid, path, "audio.mp3", "audio")
                print(f'sending audio -> {audio_sending}')
                os.remove(f'music/{get_phone(message)}/{song}')
                db.delete_downloading(sid)
                db.updateLastCommand(sid, 'audio')
                selected_adv = random.choice(adverts)
                txt = f'You song has downloaded.\n\n[*Note] {selected_adv}'
                return self.send_message(sid, txt)
            return self.send_message(sid, f'Song not found in directory music/{get_phone(message)}/{song} \n\n {random.choice(adverts)}')
        elif text.lower().startswith('lyrics'):
            # return self.send_message(sid, 'bot is under maintenance, sorry, try later')
            self.send_message(sid, 'Searching lyrics...')
            search = remove_first_word(text)

            if db.getLastCommand(sid) == 'audio':
                res = self.genius_lyrics(sid, search, get_phone(message), False)
            else:
                res = self.genius_lyrics(sid, search, get_phone(message), True)

            db.updateLastCommand(sid, 'lyrics')
            return res
        elif text.lower().startswith('adduser'):
            
            if is_group(message['chatId']):
                return self.add_participant(message['chatId'], participant_phone=remove_first_word(text))
            else:
                return self.send_message(sid, 'Cant add user here. Send this command from a group where i am an admin')
        elif text.lower().startswith('group'):
            db.updateLastCommand(sid, 'group')
            grName = remove_first_word(text).strip()
            if grName:
                self.send_message(sid, f"Creating your group called '{grName}'. Go back and check it out")
                return self.group(message['author'], grName)
            self.send_message(sid, f'Creating for you a group called "My awesome group". Go back and check it out')
            return self.group(message['author'], )
        elif text.lower().startswith('diagnose'):
            user_response = remove_first_word(text)
            db.updateLastCommand(sid, 'diagnose')

            if not user_response:
                delete_diagnosis_user(message)
                resp = self.diagnose(message['author'], sid, 'ok')
            else:
                delete_diagnosis_user(message)
                resp = self.diagnose(message['author'], sid, user_response)
            return resp
        else:
            if text == '0':
                if db.getLastCommand(sid) == 'diagnose':
                    delete_diagnosis_user(message)
                    self.diagnose(message['author'], sid, 'ok')
                db.updateLastCommand(sid, 'join')
                return ''
            # check if the user is using diagnosis command
            if db.getLastCommand(sid) == 'diagnose':
                if is_group(message['chatId']):
                    return ''
                res = self.diagnose(message['author'], sid, text.lower())
                if 'conditions were discovered' in res:
                    delete_diagnosis_user(message)
                    return self.send_message(sid, 'Thanks for using our service. \n\nSend *diagnose* to restart')
            elif db.getLastCommand(sid) == 'translation-language':
                try:
                    choice = int(text)
                    if choice in range(1, len(languages_list) + 1):
                        term = db.get_translating_text(get_phone(message))
                        self.send_message(sid, 'Translating, please wait...')
                        translation = transFr(term[1], language_code[choice-1])
                        db.updateLastCommand(sid, 'join')
                        return self.send_message(sid, translation)
                    else:
                        return ""
                except ValueError:
                    return ""
            elif db.getLastCommand(sid) == 'translation-text':
                print("Getting translation text")
                db.updateLastCommand(sid, 'translation-language')
                db.update_translating(get_phone(message), text)
                return self.send_message(sid, f"Select the language to translate to\n\n{get_languages_as_text(languages_list)}")
            elif db.getLastCommand(sid) == 'choice how-to':
                try:
                    choice = int(text)
                    user_search = db.get_how_to_search(sid)
                    if choice in range(user_search[2] + 1):
                        self.send_message(sid, 'Searching, please wait...')
                        reply = search_howto_index(user_search[1], choice-1)
                        return self.send_message(sid, reply)
                    else:
                        return ''
                except ValueError:
                    return ''
            elif db.getLastCommand(sid) == 'audio':
                try:
                    choice = int(text)
                    if choice not in range(1, 6):
                        return ''
                except ValueError:
                    return ''
                self.send_message(sid, "Downloading your song... please wait")
                db.add_downloading_user(sid)
                downloader = Downloader(sid, choice)
                audio_name = downloader.download_audio()

                # audio_name = Converter(path).convert()
                path = f'{heroku_url}files/music/{get_phone(message)}/{audio_name}'
                # path = f'localhost:5000/files/music/{get_phone(message)}/{audio_name}'
                folder = f'music/{get_phone(message)}'
                if os.path.exists(f'music/{get_phone(message)}/{audio_name}'):
                    audio_sending = self.send_file(sid, path, "audio.mp3", "audio")
                    print(f'sending audio -> {audio_sending}')
                    for file in os.listdir(folder):
                        file_path = os.path.join(folder, file)
                        if file_path.startswith('YOUTUBE_LINKS'):
                            continue
                        # os.unlink(file_path)
                    db.delete_downloading(sid)
                    db.updateLastCommand(sid, 'audio')
                    selected_adv = random.choice(adverts)
                    txt = f'You song has downloaded.\n\n[*Note] {selected_adv}'
                    return self.send_message(sid, txt)
                return self.send_message(sid,
                                         f'Song not found in directory music/{get_phone(message)}/{audio_name} \n\n '
                                         f'{random.choice(adverts)}')
            return ''
