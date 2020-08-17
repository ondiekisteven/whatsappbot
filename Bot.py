import requests
from json import dumps
from genius import Genius
from whatsappHandler import search_lyrics, register, remove_first_word, is_group
import uuid


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
        return answer.json()

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
        print(f'file -> id: {data["chatId"]}, body: {data["body"]}, filename: {data["filename"]}')
        answer = self.send_requests('sendFile', data)
        return answer

    def welcome(self, chat_id):
        welcome_string = """Hi, use these commands to control me
        Commands:
        1. Lyrics   - Get lyrics of song eg 'lyrics work - rihanna'
        2. Diagnose - Get self diagnosis service.
        3. Group    - Create a group using the bot
        4. Commands - Display this menu
        """
        return self.send_message(chat_id, welcome_string)

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

        return self.send_message(chat_id, text)

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
                if text.lower().startswith('commands'):
                    return self.welcome(sid)
                elif text.lower().startswith('menu'):
                    return self.welcome(sid)
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
