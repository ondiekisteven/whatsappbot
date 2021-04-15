from flask import Flask, request, send_file
from whatsappHandler import save_chat, getAllowedChats
import Bot
from tasks import conn
from rq import Queue
import logging

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

# r = redis.Redis()
q = Queue(connection=conn)


@app.route('/', methods=['GET'])
def test():
    return {"success": "API is working"}


@app.route('/whatsapp/', methods=['POST'])
def hello_world():

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
            q.enqueue(save_chat, bot, message)
            
            return 'Saving user'

        elif message['chatId'] in allowed_chats and not message['fromMe'] and not message['chatId'] in blocked_chats:
            logging.info(f'NEW MESSAGE FROM {message["chatId"]}: ({message["chatName"]}) ')
            logging.info(f'-----------------------------------------------')
            logging.info({message["body"]})
            logging.info('Adding task to queue...')
            job = q.enqueue(bot.processing)
            return f'Added {job.id} to queue. {len(q)} jobs in the queue currently...'
        else:
            return ""


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
            logging.info(f'NEW MESSAGE FROM {message["chatId"]}: ({message["chatName"]}) ')
            logging.info(f'-----------------------------------------------')
            logging.info({message["body"]})
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
