import random

import magic
import requests
from wikipedia import PageError, DisambiguationError

from dl import *
from genius import Genius
from twitter import twitter_dl
from whatsappHandler import register, remove_first_word, is_group
import uuid
import os
import db
from wiki import page, search_howto, search_howto_index, random_how_to
from spotdl.command_line.core import Spotdl
from dict import meaningSynonym, transFr, find_links, get_languages_as_text, languages_list, \
    language_code, get_tld
from audio import S3Uploader
from dotenv import load_dotenv


load_dotenv()

adverts = [
    'To download a video from twitter, send the link here, you will get the video in few seconds'
]
# os.environ["API_URL"] = 'https://api.chat-api.com/instance279019/'
# os.environ["API_TOKEN"] = '21lamw2k30b9f6c3'
# os.environ["HEROKU_URL"] = 'http://localhost:5000/'
heroku_url = os.getenv('BOT_HOST', 'http://173.230.134.76:8003/')  # address of this machine
api_url = "https://portal.somwaki.com/qr/send-message"
upload_url = "https://portal.somwaki.com/qr/upload-file/"
api_token = os.environ.get("API_TOKEN")
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def get_phone(message):
    return message['author'].replace('@c.us', '')


def sim(message: str):
    phone = message.split(' ')[0]
    arg = remove_first_word(message)
    if '@' in phone:
        body = {
                "body": arg,
                "fromMe": False,
                "author": phone,
                "chatId": phone,
                "chatName": phone}
    else:
        body = {
                "body": arg,
                "fromMe": False,
                "author": f"254{phone[1:]}@c.us",
                "chatId": f"254{phone[1:]}@c.us",
                "chatName": f"254{phone[1:]}"}

    

    bot = WaBot(body)
    print(f"phone: {phone}")
    print(f"arg: {arg}")
    print(f"body: {body}")

    return bot.processing()


link = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)


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

        headers = {
            'content-type': 'application/json',
            'client_id': self.message.get('client_id'),
            'auth-key': '5ohsRCA8os7xW7arVagm3O861lMZwFfl'
        }
        if method == 'sendMessage':
            d = {
                'chat_id': data['chatId'],
                'message': data['body'],
                'type': 'chat'
            }
            print(f"sending message: headers -> {headers} , data -> {d}")
            answer = requests.post(api_url, data=dumps(d), headers=headers)
        elif method == 'sendFileLink':
            # first upload the file
            # requests.post(upload_url, files={'file': open()})
            # then send message containing the file
            d = {
                'chat_id': data['chatId'],
                'message': data['message'],
                'image': data['image'],
                'type': 'file'
            }
            answer = requests.post(api_url, data=dumps(d), headers=headers)

        else:
            answer = "Not sent..."
        y = answer.text
        print(f"SEND-MESSAGE RESP: {y}")
        return y

    def send_message(self, chat_id, text):
        data = {
            'chatId': chat_id,
            'body': text
        }
        answer = self.send_requests('sendMessage', data)
        return answer

    def upload_file(self, file_path, absolute=False):

        # if absolute:
        #     files = {
        #         'file': open(file_path, 'rb')
        #     }
        # else: 
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        upload_file_name = os.path.join(BASE_DIR, file_path)
        
        logger.warning("-----------------uploading file---------------------")
        logger.warning(f"FILE -> {file_path}")
        logger.warning(f"upload_path -> {upload_file_name}")
        if not os.path.exists(upload_file_name):
            logger.error("Upload file not found. Quitting...")
            return 500
        logger.info(f"uploading {file_path}...")
        files = {
            'file': open(upload_file_name, 'rb')
        }

        headers = {
            'content-type': 'application/json',
            'client_id': self.message.get('client_id'),
            'auth-key': '5ohsRCA8os7xW7arVagm3O861lMZwFfl'
        }

        r = requests.post(url=upload_url, files=files, json={}, headers=headers)
        logger.info(f"UPLOADING FILE... {r.status_code} :: {r.text}")
        return r.status_code

    def send_file(self, chat_id, body, file_name, caption):
        if re.match(link, body):
            data = {
                'chatId': chat_id,
                'image': body,
                'message': file_name,
                'caption': caption
            }
            logger.warning(f'send_file data -> {data}')
            answer = self.send_requests('sendFileLink', data)
        else:
            status = self.upload_file(body, absolute=True)
            if status == 200:
                data = {
                    'chatId': chat_id,
                    'image': file_name,
                    'message': file_name,
                    'caption': caption
                }
                logger.warning(f'send_file data -> {data}')
                answer = self.send_requests('sendFileLink', data)
            else:
                answer = self.send_message(chat_id, 'An error occurred when uploading your file to whatsapp. '
                                                    'We will try again later')

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
Services currently offered:

1. *Lyrics*   - Get lyrics of song 
e.g. *lyrics work - rihanna*

2. *audio*    - Get audio of a song.
e.g. *audio alan walker faded*

3. *wiki* - search wikipedia for a given topic
eg. _wiki coronavirus_

4. *how to ...* - how to do something
eg _how to bake a cake_

5. To download a video from twitter, send the twitter link here

    """

        text = f'{name} \n{welcome_string}'
        self.send_message(chat_id, text)
        return self.send_message(chat_id, 'You can now download videos from twitter, just send the link here and get the video in few seconds')

    def genius_lyrics(self, chat_id, search, phone, download=False, ):
        try:
            bot = Genius()
            sid = bot.search_song(search)
            if 'Could not find' in sid:
                return 'Could not find song'
            song_id = sid['song_id']
            lyrics = bot.lyrics(song_id)
            thumbnail = sid['song_thumbnail']
            name = sid['song_title']
            self.send_file(chat_id, thumbnail, sid['song_title'] + '.jpg', name)
            text = f'{lyrics}'
        except IndexError:
            text = "Could not find lyrics"

        return self.send_message(chat_id, text)

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

        sid: str = message['chatId']
        name = message['author']
        links = find_links(text)

        env_groups = os.environ.get('WHITELISTED_GROUPS')
        white_listed_groups = env_groups.split(',') if env_groups else []

        if sid.endswith('@g.us') and sid not in white_listed_groups:
            print(f"GROUP NOT WHITELISTED\ngroup :: {sid}\nwhitelist :: {white_listed_groups}\n")
            return ""
        if not os.path.exists(f'music/{get_phone(message)}'):
            os.mkdir(f'music/{get_phone(message)}')
        if links:
            for link in links:
                if get_tld(link) in ['https://youtu.be/', 'https://www.youtube.com/', 'youtu.be', 'www.youtube.com']:
                    self.send_message(sid, 'Checking youtube link...')
                    song_title = YoutubeDL().extract_info(link, download=False)['title']
                    self.send_message(sid, f'Detected song: *{song_title}*\n\nDownloading song...')
                    audio_name = download_song(link)
                    # s3_path = save_to_s3(audio_name)
                    # logger.warning(f'SENDING AUDIO FROM {s3_path}')
                    audio_sending = self.send_file(sid, f'music/{song_title}.mp3', song_title, song_title)
                    logger.warning(audio_sending)
                    # logger.warning("DELETING FILE")
                    # S3Uploader().delete_file(s3_path)
                    return ''
                elif get_tld(link) in ['https://twitter.com/']:

                    file_path = twitter_dl(get_phone(message), link.split('?')[0])
                    file_name = file_path.split("/")[-1]
                    self.send_file(sid, file_path, file_name, file_name)
            return 'probably no youtube link'
        if text.lower().startswith('command') or text.lower().startswith('help'):
            # self.send_typing(sid)
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
            # self.send_typing(sid)
            term = remove_first_word(text)
            meaning = meaningSynonym(term)
            return self.send_message(sid, meaning)

        elif text.lower().startswith('wiki'):
            # self.send_typing(sid)
            search = remove_first_word(text)
            self.send_message(sid, f"Searching for {search}...")
            try:
                res = page(search)
                return self.send_message(sid, f'*{res["t"]}* \n\n{res["d"]}')
            except PageError:
                return self.send_message(sid,
                                         f"The page you searched  wasn't found. Use the wiki command to search about a topic, not to ask the bot random questions.',")
            except DisambiguationError as e:
                print(e)
                return self.send_message(sid, f"ERROR: {e}")
        elif text.lower().startswith('how to'):
            # self.send_typing(sid)
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

        elif text.lower().split(" ")[0] in ['audio', '.play']:
            # self.send_typing(sid)
            db.updateLastCommand(sid, 'audio')
            search = remove_first_word(text)
            if not search:
                return self.send_message(sid,
                                         'To download audio, write audio then the name of the song or audio then a '
                                         'youtube link.')
            links = find_links(search)
            if links:
                self.send_message(sid, 'Checking link...')
                for link in links:
                    if get_tld(link) in ['https://youtu.be/', 'https://www.youtube.com/', 'youtu.be',
                                         'www.youtube.com']:
                        audio_name = download_song(link)
                        path = f'{heroku_url}files/music/{audio_name}'
                        if os.path.exists(f'music/{get_phone(message)}/{audio_name}'):
                            audio_sending = self.send_file(sid, path, "audio.mp3", "audio")
                            logger.warning(f'sending audio -> {audio_sending}')

                            db.delete_downloading(sid)
                            db.updateLastCommand(sid, 'audio')
                            # selected_adv = random.choice(adverts)
                            # txt = f'You song has downloaded.\n\n[*Note] {selected_adv}'
                            # return self.send_message(sid, txt)
                            return 'DONE'
                        break
                return 'probably no youtube link'
            else:
                ytsearch = MySearch(search, get_phone(message)).get_printable()
                return self.send_message(sid, ytsearch)

        elif text.lower().startswith('dl'):
            # return self.send_message(sid, "No audio right now")
            # self.send_typing(sid)
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
                    if get_tld(link) in ['https://youtu.be/', 'https://www.youtube.com/', 'youtu.be',
                                         'www.youtube.com']:
                        audio_name = download_song(link)
                        s3_path = save_to_s3(audio_name)
                        logger.warning(f'SENDING AUDIO FROM {s3_path}')
                        audio_sending = self.send_file(sid, s3_path, audio_name, audio_name)
                        logger.warning(audio_sending)
                        logger.warning("DELETING FILE")
                        S3Uploader().delete_file(s3_path)
                        return ''
                return 'probably no youtube link'
            else:
                ytsearch = MySearch(search, get_phone(message)).get_printable()
                return self.send_message(sid, ytsearch)

        elif text.lower().startswith('lyrics'):
            # self.send_typing(sid)
            # return self.send_message(sid, 'Lyrics not available right now, try later..')
            try:
                self.send_message(sid, 'Searching lyrics...')
                search = remove_first_word(text)

                if db.getLastCommand(sid) == 'audio':
                    res = self.genius_lyrics(sid, search, get_phone(message), False)
                else:
                    res = self.genius_lyrics(sid, search, get_phone(message), True)

                db.updateLastCommand(sid, 'lyrics')
                return res
            except Exception as e:
                self.send_message(sid, str(e))
        # elif text.lower().startswith('adduser'):
        #     # self.send_typing(sid)
        #     if is_group(message['chatId']):
        #         return self.add_participant(message['chatId'], participant_phone=remove_first_word(text))
        #     else:
        #         return self.send_message(sid, 'Cant add user here. Send this command from a group where i am an admin')
        # elif text.lower().startswith('group'):
        #     # self.send_typing(sid)
        #     db.updateLastCommand(sid, 'group')
        #     grName = remove_first_word(text).strip()
        #     if grName:
        #         self.send_message(sid, f"Creating your group called '{grName}'. Go back and check it out")
        #         return self.group(message['author'], grName)
        #     self.send_message(sid, f'Creating for you a group called "My awesome group". Go back and check it out')
        #     return self.group(message['author'], )
        elif text.lower().startswith('diagnose'):
            # self.send_typing(sid)
            # if is_group(sid):
            #     return self.send_message(sid, "Diagnosis is meant to be confidential. Use it in the bot's inbox")
            user_response = remove_first_word(text)
            db.updateLastCommand(sid, 'diagnose')

            if not user_response:
                try:
                    delete_diagnosis_user(message)
                    resp = self.diagnose(message['author'], sid, 'ok')
                except:
                    resp = ""
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
            last_commad = db.getLastCommand(sid)
            if last_commad == 'diagnose':
                if is_group(message['chatId']):
                    return ''
                res = self.diagnose(message['author'], sid, text.lower())
                if 'conditions were discovered' in res:
                    delete_diagnosis_user(message)
                    return self.send_message(sid, 'Thanks for using our service. \n\nSend *diagnose* to restart')

            elif last_commad == 'translation-language':
                try:
                    choice = int(text)
                    if choice in range(1, len(languages_list) + 1):
                        term = db.get_translating_text(get_phone(message))
                        self.send_message(sid, 'Translating, please wait...')
                        translation = transFr(term[1], language_code[choice - 1])
                        db.updateLastCommand(sid, 'join')
                        return self.send_message(sid, translation)
                    else:
                        return ""
                except ValueError:
                    return ""

            elif last_commad == 'translation-text':
                print("Getting translation text")
                db.updateLastCommand(sid, 'translation-language')
                db.update_translating(get_phone(message), text)
                return self.send_message(sid,
                                         f"Select the language to translate to\n\n{get_languages_as_text(languages_list)}")

            elif last_commad == 'choice how-to':
                # self.send_typing(sid)
                try:
                    choice = int(text)
                    user_search = db.get_how_to_search(sid)
                    if choice in range(user_search[2] + 1):
                        self.send_message(sid, 'Searching, please wait...')
                        reply = search_howto_index(user_search[1], choice - 1)
                        return self.send_message(sid, reply)
                    else:
                        return ''
                except ValueError:
                    return ''

            elif last_commad == 'audio':
                # return
                # self.send_typing(sid)
                try:
                    choice = int(text)
                    if choice not in range(1, 11):
                        return ''
                except ValueError:
                    return ''

                cm = [f'downloading...', f'downloading song...', '', '', '',
                      f'please wait...', 'Your song is downloading']
                custom_msg = random.choice(cm)
                self.send_message(sid, custom_msg)
                db.add_downloading_user(sid)
                downloader = Downloader(get_phone(message), choice)
                info = YoutubeDL().extract_info(downloader.url, download=False)
                duration = info['duration']
                if duration > 1300:
                    logging.warning('SONG TOO LONG TO DOWNLOAD...')
                    return self.send_message(sid, 'This song is large. Cannot complete downloading')
                logger.warning('[*] DOWNLOADING AUDIO... ')
                try:
                    audio_name = downloader.download_audio(info)

                    # ------------------------------------------------------------------------------------
                #     s3_path = save_to_s3(audio_name)
                #     logger.warning(f'SENDING AUDIO FROM {s3_path}')
                #     audio_sending = self.send_file(sid, s3_path, audio_name, audio_name)
                #     logger.warning(audio_sending)
                #     logger.warning("DELETING FILE")
                #     S3Uploader().delete_file(s3_path)
                #     return ''
                except Exception as e:
                    self.send_message(sid, str(e))
                    return str(e)

                # ------------------------------------------------------------------------------------

                path = f'music/{get_phone(message)}/{audio_name}'
                logger.warning(f'path -> {path}')

                print("Path exists")
                audio_sending = self.send_file(sid, path, audio_name, audio_name)
                logger.warning(f'sending audio -> {audio_sending}')

                return audio_sending

            return ''

    def how_to(self, text: str, sid: str):
        # self.send_typing(sid)
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
