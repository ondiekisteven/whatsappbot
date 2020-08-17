from flask import Flask, request
from whatsappHandler import send_, register, search_lyrics
import Bot
import time


app = Flask(__name__)


@app.route('/whatsapp/twilio/messages', methods=['POST', 'GET'])
def hello_world():
    if request.method == 'POST':
        message = request.form['Body']
        sender = request.form['From']
        print(f'message from {sender}: {message}')
        numeric_filter = filter(str.isdigit, sender)
        numeric_string = "".join(numeric_filter)

        if message.lower().startswith("lyrics"):
            print(message.lower())
            result = search_lyrics(message)
            return send_(sender, result)
        else:
            response = register(numeric_string, message)
            return send_(sender, response)


@app.route('/whatsapp/chatapi/messages', methods=['POST'])
def receive():
    bot = Bot.WaBot(request.json)
    messages = bot.dict_message

    allowed_chats = ['MAJANGO ⌨🖥', 'Som']
    for message in messages:
        if not message['fromMe']:
            print(f'Message from {request.json["messages"][0]["chatName"]}: {request.json["messages"][0]["body"]}')
        if message['chatName'] in allowed_chats and not message['fromMe']:
            return bot.processing()
        else:
            return ""


if __name__ == '__main__':
    app.run()
