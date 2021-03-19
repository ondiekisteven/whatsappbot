from flask import Flask, request, send_file
from whatsappHandler import save_chat, getAllowedChats
import Bot
import logging
logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)


@app.route('/', methods=['GET'])
def test():
    return {"success": "API is working"}


@app.route('/whatsapp/twilio/messages', methods=['POST', 'GET'])
def hello_world():
    pass
    # if request.method == 'POST':
    #     message = request.form['Body']
    #     sender = request.form['From']
    #     print(f'message from {sender}: {message}')
    #     numeric_filter = filter(str.isdigit, sender)
    #     numeric_string = "".join(numeric_filter)

    #     if message.lower().startswith("lyrics"):
    #         print(message.lower())
    #         result = search_lyrics(message)
    #         return send_(sender, result)
    #     else:
    #         response = register(numeric_string, message)
    #         return send_(sender, response)


@app.route('/whatsapp/chatapi/messages/', methods=['POST'])
def receive():
    messages = request.json['messages']
    allowed_chats = getAllowedChats()
    blocked_chats = [
        '254702381629-1608391772@g.us', '254738239601-1609837284@g.us', '254716736857-1506316355@g.us'
    ]
    for message in messages:
        bot = Bot.WaBot(message)

        if message['body'].lower() == 'join bot':
            logging.info("NEW USER REGISTERING")
            logging.info(message)
            return save_chat(bot, message)

        elif message['chatId'] in allowed_chats and not message['fromMe'] and not message['chatId'] in blocked_chats:
            logging.info(f'NEW MESSAGE FROM {message["chatId"]}')
            logging.info(f'-----------------------------------------------')
            logging.info({message["body"]})
            logging.info(f'-----------------------------------------------')
            return bot.processing()
        else:
            return ""


@app.route('/files/music/<filename>/', methods=['GET'])
def download_audio(filename):
    file_path = f'music/{filename}'
    logging.info(file_path)
    if not file_path:
        return 'File not found'
    return send_file(file_path, as_attachment=True)


if __name__ == '__main__':
    app.run()
