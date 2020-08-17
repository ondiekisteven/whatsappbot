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
    print(f'Message from {request.json["messages"][0]["chatName"]}: {request.json["messages"][0]["body"]}')
    bot = Bot.WaBot(request.json)
    messages = bot.dict_message
    for message in messages:
        if message['chatName'] == 'Som' and not message['fromMe']:
            bot.processing()
            time.sleep(4)
            msg = """
            Select option:
            lyrics   - get lyrics of song eg 'lyrics work - rihanna'
            diagnose - get self diagnosis service.
            group    - create a group using the bot
            menu     - go back to main menu
            """
            return bot.send_message(message['chatId'], msg)
        else:
            return ""


if __name__ == '__main__':
    app.run()
