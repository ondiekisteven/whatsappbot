from flask import Flask, request, send_file, jsonify
from whatsappHandler import save_chat, getAllowedChats
import Bot
from tasks import conn
from rq import Queue
import logging
import rq_dashboard

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)

app.config.from_object(rq_dashboard.default_settings)
app.register_blueprint(rq_dashboard.blueprint, url_prefix="/rq")


q = Queue(connection=conn)


@app.route('/', methods=['GET'])
def test():
    return {"success": "API is working"}


@app.route('/pay/confirmation/', methods=['GET', 'POST'])
def confirmation():
    if request.method == 'POST':
        print("received data")
        print(request.json)
        context = {
            'ResultCode': 0,
            'ResultDesc': 'Accepted'
        }
        return jsonify(context)
    return jsonify(message='confirmation page')


@app.route('/pay/validation/', methods=['GET', 'POST'])
def validation():
    if request.method == 'POST':
        print("received data")
        print(request.json)
        context = {
            'ResultCode': 0,
            'ResultDesc': 'Accepted'
        }
        return jsonify(context)
    return jsonify(message='validation page')


@app.route('/whatsapp/', methods=['POST'])
def hello_world():

    messages = request.json['messages']
    allowed_chats = getAllowedChats()
    blocked_chats = [

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
            job = q.enqueue(bot.processing)
            logging.info(f'Added {job.id} to queue. {len(q)} jobs in the queue currently...')
            return f'Added {job.id} to queue. {len(q)} jobs in the queue currently...'
        else:
            return ""


@app.route('/whatsapp/chatapi/messages/', methods=['POST'])
def receive():
    messages = request.json['messages']
    allowed_chats = getAllowedChats()
    blocked_chats = [
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
    file_path = f'/tmp/music/{filename}'
    logging.info(file_path)
    if not file_path:
        return 'File not found'
    return send_file(file_path, as_attachment=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8003)
