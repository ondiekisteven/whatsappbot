import requests
from json import dumps
from genius import Genius, get_song
from whatsappHandler import register, remove_first_word, is_group
import uuid
import os
import db
import random
from spotdl.command_line.core import Spotdl


adverts = [
    'I you dont receive your song quickly, send the command *join bot* to refresh the bot. It will send your song',
    'Audio downloads are not stable yet, Dont download many songs in a short time, it will crash the bot',
    'Remember whatsapp has a size limit. Therefore, dont download dj mixes and other big files, They wont be sent here',
    'Lyrics are not guaranteed to be exactly as you wanted. Most songs\' lyrics are not recorded.',
    'The bot downloads songs from spotify and youtube. If we didnt find your song, its probably not in youtube yet',
    'You can get self diagnosis by typing *Diagnose start*',
    'If you have trouble using the bot, contact the developer here: 0790670635. ',
    'The bot is under testing, some features may not work perfect, be patient with them',
    'If you want to join in developing the bot, contact here: 0790670635',
    'Sometimes audios can take up to one minute to deliver on your phone, be patient',
    ''
]


def get_phone(message):
    return message['author'].replace('@c.us', '')


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
    answer = requests.post('https://eu173.chat-api.com/instance163153/sendPTT?token=18tge8h634rmjh5t', data=data)

    return answer


class WaBot:

    def __init__(self, json):
        self.json = json
        self.dict_message = json['messages']
        self.APIUrl = 'https://eu172.chat-api.com/instance164092/'
        self.token = 'zzceflkpr5jy8ee9'
        self.last_command = "last command"

    def get_last_command(self):
        pass

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

    def download_audio(self, song, user):
        path = f'music/{user}'
        if not os.path.exists(path):
            print("Directory not found, Creating...")
            os.mkdir(path)
        args = {
            "song": [song],
            'output_file': path + '/{artist} - {track-name}.{output-ext}'
        }
        print(f'Downloading {song}')
        self.send_message(f'{user}"c.us', 'Downloading your song...')
        with Spotdl(args) as spotdl_handler:
            spotdl_handler.match_arguments()

        return path

    def welcome(self, chat_id, name):
        welcome_string = """Hi, use these commands to control me
    Commands:
    [Music channel]
    *Lyrics*   - Get lyrics of song 
    
    example
    *lyrics work - rihanna*
    
    
    *audio*    - Get audio of a song. write audio
    
    example
    *audio alan walker faded* or
    *audio http//youtube.com...* (youtube link)
    
                    
                    
    [health]
    *Diagnose* - Get self diagnosis service
    
    example:
    *diagnose i feel pain in my back*
    
    
    *Group* -Create a group using the bot. it adds the bot as a user
    
    *Commands* or *help* -Display this menu
    """

        text = f'{name} \n{welcome_string}'
        return self.send_message(chat_id, text)

    def genius_lyrics(self, chat_id, search, phone, download=False, ):
        bot = Genius()
        sid = bot.search_song(search)
        if 'Could not find' in sid:
            return 'Could not find song'
        song_id = sid['song_id']
        lyrics = bot.retrieve_lyrics(song_id)
        thumbnail = sid['song_thumbnail']
        name = sid['song_title']
        self.send_file(chat_id, thumbnail, uuid.uuid4().hex+'.jpg', name)
        text = f'TITLE: {name}\n\n{lyrics}'

        message_send = self.send_message(chat_id, text)
        if download:
            path = self.download_audio(search, phone)
            song = get_song(path)
            if song == 'empty directory':
                db.delete_downloading(sid)
                return self.send_message(sid, 'Song not found in Directory')
            path = f'https://som-whatsapp.herokuapp.com/files/music/{phone}/{song}'
            if path == 'File not found':
                return self.send_message(sid, 'Error serving your song')
            audio_sending = self.send_file(sid, path, "audio.mp3", "audio")
            print(f'sending audio -> {audio_sending}')
            if os.path.exists(f'music/{phone}/{song}'):
                os.remove(f'music/{phone}/{song}')
                db.delete_downloading(sid)
                db.updateLastCommand(sid, 'audio')

                return self.send_message(sid, f'Your song has downloaded. If you dont receive it quickly, send the '
                                              f'command *join bot* to refresh the bot. It will send your song')
            return self.send_message(sid, 'An error occurred. type help.\n You can contact 0790670635 to report')
            # path = download_audio(name, phone, bot)
            # audio = get_song(path)
            # audio_path = f'https://som-whatsapp.herokuapp.com/files/music/{phone}/{audio}'
            # audio_sending = self.send_file(chat_id, audio_path, uuid.uuid4().hex + "audio.mp3", "audio")
            # print(f'sending audio -> {audio_sending}')
            # os.remove(f'music/{phone}/{audio}')

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

    def group(self, author):
        phone = author.replace('@c.us', '')
        data = {
            "groupName": 'Group with the bot Python',
            "phones": phone,
            'messageText': 'It is your group. Enjoy'
        }
        answer = self.send_requests('group', data)
        return answer

    def add_participant(self, group_id, participant_phone=None, participant_id=None, ):
        data = {
            'groupId': group_id
        }
        if participant_phone:
            data['participantPhone'] = participant_phone
        elif participant_id:
            data['participantChatId'] = participant_id
        else:
            return 'Missing user to add'
        ans = self.send_requests('addGroupParticipant', data)

        return self.send_message(group_id, ans['message'])

    def processing(self):
        if self.dict_message:
            for message in self.dict_message:
                text = message['body']

                sid = message['chatId']
                name = message['author']
                if text.lower().startswith('command') or text.lower().startswith('help'):
                    db.updateLastCommand(sid, 'help')
                    return self.welcome(sid, name)

                # for downloading audio from youtube or spotify or elsewhere
                elif text.lower().startswith('audio'):
                    # return self.send_message(sid, 'bot is under maintenance. sorry. try later')
                    if db.is_downloading(sid):
                        try:
                            files = get_song(f'music/{get_phone(message)}')
                            if files == 'empty directory':
                                db.delete_downloading(sid)
                            else:
                                return self.send_message(sid, 'Wait for last song to download')
                        except FileNotFoundError:
                            os.mkdir('music/{get_phone(message)}')

                    db.add_downloading_user(sid)
                    search = remove_first_word(text)
                    bot = Genius()

                    path = self.download_audio(search, get_phone(message))
                    song = get_song(path)
                    if song == 'empty directory':
                        db.delete_downloading(sid)
                        return self.send_message(sid, 'Error downloading song')
                    path = f'https://som-whatsapp.herokuapp.com/files/music/{get_phone(message)}/{song}'
                    audio_sending = self.send_file(sid, path, "audio.mp3", "audio")
                    print(f'sending audio -> {audio_sending}')
                    if os.path.exists(f'music/{get_phone(message)}/{song}'):
                        os.remove(f'music/{get_phone(message)}/{song}')
                        db.delete_downloading(sid)
                        db.updateLastCommand(sid, 'audio')
                        selected_adv = random.choice(adverts)
                        txt = f'You song has downloaded.\n\n[*Note]{selected_adv}'
                        return self.send_message(sid, txt)
                    return self.send_message(sid, 'An error occurred. type help.\n You can contact 0790670635 to report')
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
                        return self.add_participant(message['chatId'], text)
                    else:
                        return 'Cant add user here'
                elif text.lower().startswith('group'):
                    db.updateLastCommand(sid, 'audio')
                    return self.group(message['author'])
                elif text.lower().startswith('diagnose'):
                    response = remove_first_word(text)
                    db.updateLastCommand(sid, 'diagnose')
                    if response.strip() == 'start' or None:
                        # check if
                        self.send_message(sid, 'Let\'s continue where we left')
                        if db.getFinishedRegistration(get_phone(message)):
                            if db.getCurrentQuestion(get_phone(message)) is not None:
                                res = f'{db.getCurrentQuestion(get_phone(message))[2]}\n\n1 - Yes\n2 - No\n0 - Cancel ' \
                                      f'diagnosis and restart '
                                return self.send_message(sid, res)
                            else:
                                self.send_message(sid, 'How are you feeling today? Describe your condition')
                        else:
                            self.send_message(sid, db.getQuestion(db.getCurrentCount(get_phone(message))))
                    elif response.strip() == 'restart':
                        print('We need to restart diagnosis using the provided condition')
                        delete_diagnosis_user(message)

                        register(get_phone(message), 'OK')
                        return self.diagnose(message['author'], sid, response.strip())

                else:
                    if is_group(message['chatId']):
                        return ''
                    # check if the user is using diagnosis command
                    if db.getLastCommand(sid) == 'diagnose':
                        res = self.diagnose(message['author'], sid, text.lower())
                        if 'conditions were discovered' in res:
                            delete_diagnosis_user(message)
                            self.send_message(sid, 'Thanks for using our service. \n\nSend *diagnose* to restart')
                    return ''
