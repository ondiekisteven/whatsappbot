import requests
from json import dumps
from whatsappHandler import search_lyrics, register, remove_first_word, is_group


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

                id = message['chatId']
                if text.lower().startswith('hi'):
                    return self.welcome(id)
                elif text.lower().startswith('menu'):
                    return self.welcome(id)
                elif text.lower().startswith('lyrics'):
                    return self.lyrics(id, text)
                elif text.lower().startswith('adduser'):
                    if is_group(message['chatId']):
                        print('adding user')
                        user_to_add = remove_first_word(text)
                        return self.add_participant(message['chatId'], user_to_add)
                    else:
                        return 'Cant add user here'
                elif text.lower().startswith('group'):
                    return self.group(message['author'])
                elif text.lower().startswith('diagnose'):
                    print(f'message to diagnosis: {text}')
                    text = remove_first_word(text)
                    return self.diagnose(message['author'], id, text)
                else:
                    return ''
