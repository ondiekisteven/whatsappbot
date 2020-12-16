from flask import Flask, request, send_file
from whatsappHandler import register, search_lyrics, save_chat, getAllowedChats
import Bot
from sendQueue import to_queue
from json import dumps
import tasks
from dict import find_links, ACCEPTED_LINKS, VERIFIED_USERS, get_tld
from whatsappHandler import is_group

app = Flask(__name__)


@app.route('/', methods=['GET'])
def test():
    return {"success" : "API is working"}


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
    print("processing message")
    messages = request.json['messages']
    allowed_chats = getAllowedChats()
    for message in messages:
        bot = Bot.WaBot(message)
        if not message['fromMe']:
            print(f'Message from {request.json["messages"][0]["chatName"]}: {request.json["messages"][0]["body"]}')

        if message['body'].lower() == 'join bot':
            return save_chat(bot, message)

        elif message['chatId'] in allowed_chats and not message['fromMe']:
            allowed_groups = ['254745021668-1599248192@g.us', '254745021668-1605898758@g.us']
            print(f"{message['chatId']}")
            if message['chatId'] in allowed_groups:
                if is_group(message['chatId']):
                    text = message['body']
                    links = find_links(text)
                    if links:
                        for link in links:
                            if get_tld(link) not in ACCEPTED_LINKS:
                                if link not in ACCEPTED_LINKS and message['author'] not in VERIFIED_USERS:
                                    bot.send_message(message['chatId'], "Unwanted links found. Removing user.")
                                    return bot.remove_participant(message['chatId'], participant_id=message['author'])

            return bot.processing()
        else:
            return ""


@app.route('/files/music/<sid>/<filename>', methods=['GET'])
def download_audio(sid, filename):
    file_path = f'music/{sid}/{filename}'
    if not file_path:
        return 'File not found'
    return send_file(file_path, as_attachment=True)


if __name__ == '__main__':
    app.run()
