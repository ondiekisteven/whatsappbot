from flask import Flask, request, send_file
from whatsappHandler import send_, register, search_lyrics, save_chat, getAllowedChats
import Bot
from sendQueue import to_queue
from json import dumps
import tasks

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
    messages = request.json['messages']
    allowed_chats = getAllowedChats()
    for message in messages:
        bot = Bot.WaBot(request.json)
        if not message['fromMe']:
            print(f'Message from {request.json["messages"][0]["chatName"]}: {request.json["messages"][0]["body"]}')

        if message['body'].lower() == 'join bot':
            return save_chat(bot, message)
        elif message['chatId'] in allowed_chats and not message['fromMe']:
            tasks.work.delay(message)
            return '[x] Sent to redis '
        else:
            return ""


@app.route('/files/music/<sid>/<filename>', methods=['GET'])
def download_audio(sid=None, filename=None):
    file_path = f'music/{sid}/{filename}'
    if not file_path:
        return 'File not found'
    return send_file(file_path, as_attachment=True)


if __name__ == '__main__':
    app.run()
