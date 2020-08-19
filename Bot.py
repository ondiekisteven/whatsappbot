import requests
from json import dumps
from genius import Genius, get_song
from whatsappHandler import register, remove_first_word, is_group
import uuid
import os
import db


def send_ppt(chat_id, audio):
    data = {
        "chatId": chat_id,
        "audio": audio
    }
    answer = requests.post('https://api.chat-api.com/instance162072/sendPTT?token=0kr1ty8zjmh66oj4', data=data)

    return answer


class WaBot:

    def __init__(self, json):
        self.json = json
        self.dict_message = json['messages']
        self.APIUrl = 'https://eu92.chat-api.com/instance162072/'
        self.token = '0kr1ty8zjmh66oj4'
        self.last_command = "last comand"

    def get_last_comand(self):
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

    def genius_lyrics(self, chat_id, search):
        bot = Genius()
        sid = bot.search_song(search)
        song_id = sid['song_id']
        lyrics = bot.retrieve_lyrics(song_id)
        thumbnail = sid['song_thumbnail']
        name = sid['song_title']
        res = self.send_file(chat_id, thumbnail, uuid.uuid4().hex+'.jpg', name)
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
        pass
        # lyrics = search_lyrics(search)
        # return self.send_message(chat_id, lyrics)

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
                if text.lower().startswith('commands') or text.lower().startswith('help'):
                    db.updateLastCommand(sid, 'help')
                    return self.welcome(sid, name)
                # for downloading audio from youtube or spotify or elsewhere
                elif text.lower().startswith('audio'):
                    search = remove_first_word(text)
                    bot = Genius()
                    bot.download_audio(search)
                    song = get_song()
                    path = f'https://som-whatsapp.herokuapp.com/files/{song}'
                    self.send_file(sid, path, "audio.mp3", "audio")
                    db.updateLastCommand(sid, 'audio')
                    return 'hi'
                elif text.lower().startswith('lyrics'):
                    search = remove_first_word(text)
                    db.updateLastCommand(sid, 'lyrics')
                    return self.genius_lyrics(sid, search)
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
                    return self.diagnose(message['author'], sid, response)
                else:
                    # check if the user is using diagnosis command
                    if db.getLastCommand(sid) == 'diagnose':
                        return self.diagnose(message['author'], sid, text.lower())
                    return ''
