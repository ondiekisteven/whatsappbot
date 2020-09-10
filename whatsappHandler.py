from twilio.rest import Client
import db
import requests
from configparser import ConfigParser
from infermedicaClient import make_chuka_api_request
from json import loads
from loadConf import get_twilio_auth_token, get_twilio_sid
from time import sleep


x = """
Hello, Here are the serivces i can offer you...

1. *Lyrics*   - Get lyrics of song 
e.g. *lyrics work - rihanna*


2. *audio*    - Get audio of a song. write audio
e.g. *audio alan walker faded* or
*audio http//youtube.com...* (youtube link)

3. *wiki* - search wikipedia for a given topic
eg. _wiki coronavirus_

4. *how to ...* - how to do something
eg _how to bake a cake_

5. *translate* - translate sentences to other languages
e.g. _translate Good morning_

6. *Group* -Create a group using the bot. it adds the bot as a user
eg. group My Music Group

*Commands* or *help* -Display this menu
    """


def sendParse(message):
    url = "https://api.infermedica.com/v2/parse"

    parser = ConfigParser()
    parser.read('configurations.ini')

    app_id = parser.get('auth', 'app_id')
    app_key = parser.get('auth', 'app_key')

    header = {
        'Content-Type': 'application/json',
        'App-Id': app_id,
        'App-Key': app_key
    }

    data = {'text': message}
    # print('[*] Sending parse request...')
    r = requests.post(url=url, json=data, headers=header)
    response = loads(r.text)

    if len(response['mentions']) == 0:
        return 'We could not understand your message'
    else:
        text = []

        for mention in response['mentions']:
            if mention['type'] == 'symptom':
                # text += '+' + mention['name'] + ' [' + mention['choice_id'] + ']\n'
                new_sym = {
                    'id': mention['id'],
                    'choice_id': mention['choice_id'],
                    'initial': True
                }
                text.append(new_sym)
        return text


# sending a whatsapp message. receiver is the number to receive the message,
def send_(receiver, text):
    account_sid = get_twilio_sid()
    auth_token = get_twilio_auth_token()
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body=text,
        from_='whatsapp:+14155238886',
        to=receiver
    )

    return message.sid


def register(tg_id, response):
    if not db.getUserById(tg_id):  # if user is not registered, register them
        db.saveUser(tg_id=tg_id, first_name="", last_name="")
        db.getUserById(tg_id)

        db.saveControlBoard(tg_id, 0)  # start a trace on control board table

    current_count = db.getCurrentCount(tg_id)

    # saving user details in database
    if current_count == 1:
        if response.lower() in ['no', '2']:
            db.deleteUser(tg_id)
            return 'Ok. Maybe later. You can continue registration by clicking /register .'
    if current_count == 2:
        if response.lower().strip() in ['male', '1']:
            db.saveGender(tg_id, 'male')
        elif response.lower().strip() == ['female', '2']:
            db.saveGender(tg_id, 'female')
        else:
            return 'Invalid gender. Try again'
    elif current_count == 3:
        try:
            age = int(response)
            if 0 < age < 120:
                db.saveAge(tg_id, age)
            else:
                return 'Invalid age'
        except ValueError:
            return 'Invalid age'
    elif current_count == 4:
        if not response:
            return 'Sorry, did you forget to write the name? Try again'
        else:
            db.saveFirstName(tg_id, response)
    elif current_count == 5:
        if not response:
            return 'Sorry, did you forget to write the name? Try again'
        else:
            db.saveLastName(tg_id, response)
            db.saveFinishedRegistration(tg_id)

    # if user has finished registration, stop asking registration questions, and control board trace
    if db.getFinishedRegistration(tg_id) is None:
        can_continue = True
    else:
        can_continue = False

    if current_count >= 6:
        pass
    else:
        db.saveControlBoard(tg_id, current_count + 1)

    # return registration question from database if user hasn't finished registering
    if can_continue:

        nextQ = db.getQuestion(current_count + 1)
        if 'our system' in nextQ:
            nextQ += '\n1 - Yes\n2 - No'
        elif '[male/female]' in nextQ:
            nextQ += '\n1 - Yes\n2 - No'
    else:
        # go to diagnosis part if registration is complete
        if db.getOnGoingUser(tg_id) is None:

            # asking user to describe condition
            db.saveOnGoingUser(tg_id)
            return 'How are you feeling today? Describe your condition'
        else:
            INVALID_INITIAL_SYMPTOM = 'Please say that again, i couldn\'t get you. \nExplain how you feel. eg, ' \
                                      '"i feel pain on my back" '
            if response.lower() == '0':
                db.deleteUserOngoingDiagnosis(tg_id)
                db.deleteUserSymptoms(tg_id)
                db.deleteUserCurrentSymptom(tg_id)
                db.deleteCurrentQuestion(tg_id)
                return 'Diagnosis stoppped. You can start by typing *diagnose start*'
            elif response.lower() in ['yes', '1']:
                if db.getCurrentQuestion(tg_id) is None:
                    return INVALID_INITIAL_SYMPTOM
                db.saveSymptom(tg_id, db.getCurrentQuestion(tg_id)[1], 'present')
            elif response.lower() in ['no', '2']:
                if db.getCurrentQuestion(tg_id) is None:
                    return INVALID_INITIAL_SYMPTOM
                db.saveSymptom(tg_id, db.getCurrentQuestion(tg_id)[1], 'absent')
            elif 'dont know' in response.lower() or 'don\'t know' in response.lower() or response.lower() == '3':
                if db.getCurrentQuestion(tg_id) is None:
                    return INVALID_INITIAL_SYMPTOM
                db.saveSymptom(tg_id, db.getCurrentQuestion(tg_id)[1], 'unknown')
            else:
                symptoms = sendParse(response)
                print(f'PARSE SYMPTOMS: {symptoms}')

                if len(symptoms) > 0 and 'understand' not in symptoms:
                    for symptom in symptoms:
                        s_id = symptom['id']
                        choice = symptom['choice_id']
                        db.saveInitialSymptom(tg_id, s_id, choice, 1)
                else:
                    if db.getCurrentQuestion(tg_id):
                        return f'Invalid answer\n\n{db.getCurrentQuestion(tg_id)[2]}\n1 - Yes\n2 - No\n3 - Dont know' \
                               f'\n\n0 - Cancel diagnosis and restart '
                    else:
                        return 'Describe how you feel. Example, I feel pain in my joints '

            symptoms = db.getSymptoms(tg_id)
            # print(f'API HANDLER symptoms: {symptoms}')
            age = db.getAge(tg_id)
            # print(f'API HANDLER age: {age}')
            sex = db.getGender(tg_id)
            sex = sex.lower()
            # print(f'API HANDLER sex: {sex}')

            response = make_chuka_api_request(age, sex, symptoms)
            # print(f'API HANDLER response: {response}')

            response = loads(response)

            if 'next_question' in response:
                nextQuestionId = response["next_question"]["items"][0]["id"]
                db.updateCurrentQuestion(tg_id, nextQuestionId, response["next_question"]["text"])
                return f'{response["next_question"]["text"]}\n1 - Yes\n2 - No\n3 - Dont know\n\n_0 - Cancel diagnosis_' \
                       f'and restart '
            elif 'stop' in response:
                conditions = response['conditions']
                message = "After Diagnosis, the following conditions were discovered:\n\n"

                for condition in conditions:
                    name = condition['name']
                    prob = float(condition['probability']) * 100
                    prob = round(prob, 2)
                    prob = f'{prob} %'

                    message += f'Name\t: {name}\nProbability: {prob}\n\n'

                return message
            else:
                return 'Could not get any response. Press /diagnose to restart.'


def getlyric(body):
    return body["lyrics"]["lyrics_body"]


def remove_first_word(text):
    words = text.split(' ')
    return " ".join(words[1:])


def is_group(chat_id):
    us, gr = chat_id.split('@')
    if 'g.us' in gr:
        return True
    else:
        return False


def search_lyrics(search):
    base_url = "http://api.musixmatch.com/ws/1.1/"
    format_url = "?format=json&callback=callback"

    endpoint = "matcher.lyrics.get"

    artist_parameter = "&q_artist="
    track_parameter = "&q_track="
    api_key = "&apikey=23511ff3cc653349eabac10c3ff2ce03"

    if '-' not in search:
        return 'invalid search, use - to separate artist from song. eg. *work - rihanna*'
    else:
        search = remove_first_word(search)
        if 'by' in search:
            track, artist = search.split('by')
            api_call = base_url + endpoint + format_url + artist_parameter + artist + track_parameter + track + api_key
            res = requests.get(api_call)
            json_res = res.json()
            body = json_res['message']['body']

            if len(body) == 0:
                return 'Song not found!'
            else:
                return getlyric(body)
        track, artist = search.split('-')

        api_call = base_url + endpoint + format_url + artist_parameter + artist + track_parameter + track + api_key

        res = requests.get(api_call)
        json_res = res.json()
        body = json_res['message']['body']

        if len(body) == 0:
            api_call = base_url + endpoint + format_url + artist_parameter + track + track_parameter + artist + api_key
            res = requests.get(api_call)
            json_res = res.json()
            sbody = json_res['message']['body']

            if len(sbody) == 0:
                return 'Song not found!'
            else:
                return getlyric(sbody)
        else:
            return getlyric(body)


def getAllowedChats():
    allowed = []
    cursor = db.getAllowedBotChat()
    for item in cursor:
        allowed.append(item[0])
    return allowed


def save_chat(bot, message):
    text = f"""
    Hello {message['chatName']}, welcome.
    Send *help* or *commands* for help
    """
    user = db.checkAllowedChatBot(str(message['chatId']))
    if user:
        return bot.send_message(message['chatId'], 'You are already registered :)')
    else:
        db.addAllowedBotChat(str(message['chatId']), message['chatName'])
        db.addLastCommand(str(message['chatId']), 'join')
        bot.send_message(message['chatId'], text)
        bot.send_message(message['chatId'], '*Please note the bot is not perfect yet, its being developed still. If '
                                            'it doesnt respond, reply with `help` to get other services then try again '
                                            'later*')
        sleep(1)

        return bot.send_message(message['chatId'], x)
