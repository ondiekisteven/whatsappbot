import requests
from json import dumps
from whatsappHandler import search_lyrics, register


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

    def welcome(self, chat_id):
        welcome_string = """Hi, use these commands to control me
        Commands:
        1. lyrics   - get lyrics of song eg 'lyrics work - rihanna'
        2. diagnose - get self diagnosis service.
        3. group    - create a group using the bot
        4. menu     - go back to main menu
        """
        return self.send_message(chat_id, welcome_string)

    def lyrics(self, chat_id, search):
        lyrics = search_lyrics(search)
        return self.send_message(chat_id, lyrics)

    def diagnose(self, author, chat_id, response):
        phone = author.replace('@c.us', '')
        reply = register(phone, response)
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

    def processing(self):
        if self.dict_message:
            for message in self.dict_message:
                text = message['body']

                id = message['chatId']
                if text.lower().startswith('hi'):
                    return self.welcome(id)
                elif text.lower().startswith('menu'):
                    return self.welcome(id)
                elif text.lower().startswith('lyrics'):
                    return self.lyrics(id, text)
                elif text.lower().startswith('group'):
                    return self.group(message['author'])
                else:
                    return self.diagnose(message['author'], id, message)

