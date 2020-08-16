from flask import Flask, request
from whatsappHandler import send_, register, search_lyrics

app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
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


@app.route('/status', methods=['POST'])
def status():
    print("received status message")
    return "hello"


if __name__ == '__main__':
    app.run()
