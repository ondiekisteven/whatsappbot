import requests
from json import dumps
from genius import Genius, get_song
from whatsappHandler import search_lyrics, register, remove_first_word, is_group
import uuid
import os


def send_ppt(chat_id, audio):
    data = {
        "chatId": chat_id,
        "audio": audio
    }
    print(f'Trying to send audio from "{audio}"')
    answer = requests.post('https://api.chat-api.com/instance162072/sendPTT?token=0kr1ty8zjmh66oj4', data=data)

    print(f'{answer.text}')
    return answer


class WaBot:

    def __init__(self, json):
        self.json = json
        self.dict_message = json['messages']
        self.APIUrl = 'https://eu92.chat-api.com/instance162072/'
        self.token = '0kr1ty8zjmh66oj4'

    def send_requests(self, method, data):
        url = f'{self.APIUrl}{method}?token={self.token}'
        headers = {'content-type': 'application/json'}
        answer = requests.post(url, data=dumps(data), headers=headers)
        y = answer.text
        print(f'MAIN REQUEST: {y}')
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

    def welcome(self, chat_id, name):
        welcome_string = """Hi, use these commands to control me
    Commands:
    [Music channel]
    1. Lyrics   - Get lyrics of song eg 'lyrics work - rihanna'
    2. audio    - Get audio of a song. write audio <name of song>
                  also audio <youtube link> will convert video from 
                    the youtube link to audio
                    
    [health]
    1. Diagnose - Get self diagnosis service
                    usage:
                    write "diagnose <your reply here>" for the bot to understand.
    
    [others]
    1. Group    - Create a group using the bot. it adds the bot as a user
    4. Commands - Display this menu
    """

        text = f'{name} \n{welcome_string}'
        return self.send_message(chat_id, text)

    def genius_lyrics(self, chat_id, search):
        bot = Genius()
        sid = bot.search_song(search)
        song_id = sid['song_id']
        print(f'song Id -> {song_id}')
        lyrics = bot.retrieve_lyrics(song_id)
        thumbnail = sid['song_thumbnail']
        print(f'song title: {sid["song_title"]}')
        name = sid['song_title']
        print(f'sending image ...{thumbnail}')
        res = self.send_file(chat_id, thumbnail, uuid.uuid4().hex+'.jpg', name)
        print(res)
        text = f'TITLE: {name}\n\n{lyrics}'

        message_send = self.send_message(chat_id, text)
        bot.download_audio(name)
        audio = get_song()
        audio_path = f'https://som-whatsapp.herokuapp.com/files/{audio}'
        audio_sending = self.send_file(chat_id, audio_path, uuid.uuid4().hex + "audio.mp3", "audio")
        print(f'sending audio -> {audio_sending}')
        os.remove(audio)
        return message_send

    def lyrics(self, chat_id, search):
        lyrics = search_lyrics(search)
        return self.send_message(chat_id, lyrics)

    def diagnose(self, author, chat_id, response):
        phone = author.replace('@c.us', '')
        reply = register(phone, response)
        print(f'diagnosis recepient:{phone}')
        return self.send_message(chat_id, reply)

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
        print('checking user ...')
        if participant_phone:
            data['participantPhone'] = participant_phone
        elif participant_id:
            data['participantChatId'] = participant_id
        else:
            return 'Missing user to add'
        print('sending request')
        ans = self.send_requests('addGroupParticipant', data)

        return self.send_message(group_id, ans['message'])

    def processing(self):
        if self.dict_message:
            for message in self.dict_message:
                text = message['body']

                sid = message['chatId']
                name = message['author']
                if text.lower().startswith('commands'):
                    return self.welcome(sid, name)
                elif text.lower().startswith('menu'):
                    return self.welcome(sid, name)
                elif text.lower().startswith('audio'):
                    search = remove_first_word(text)
                    bot = Genius()
                    bot.download_audio(search)
                    song = get_song()
                    path = f'https://som-whatsapp.herokuapp.com/files/{song}'
                    self.send_file(sid, path, "audio.mp3", "audio")
                    return 'hi'
                elif text.lower().startswith('lyrics'):
                    search = remove_first_word(text)
                    return self.genius_lyrics(sid, search)
                elif text.lower().startswith('adduser'):
                    if is_group(message['chatId']):
                        print('adding user')
                        return self.add_participant(message['chatId'], text)
                    else:
                        return 'Cant add user here'
                elif text.lower().startswith('group'):
                    return self.group(message['author'])
                elif text.lower().startswith('diagnose'):
                    print(f'message to diagnosis: {text}')
                    return self.diagnose(message['author'], sid, text)
                else:
                    return ''
