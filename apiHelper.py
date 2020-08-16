from configparser import ConfigParser
from pip._vendor import requests
from json import loads


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


def parseDatabaseSymptoms(cursor):
    x = cursor
    text = []

    for i in x:

        new_sym = {
            'id': i[2],
            'choice_id': i[3],
        }
        if i[2] == '':
            continue
        if i[4] == 1:
            new_sym['source'] = 'initial'
        text.append(new_sym)
    return text


def extractNextQuestion(response):
    false = False
    response = response.__dict__
    n = {
        'text': response['question']['text'],
        'id': response['question']['items'][0]['id']
    }
    return n


def sendDiagnosis(age, sex, symptoms):
    url = "https://api.infermedica.com/v2/diagnosis"

    body = {
        "sex": sex,
        "age": age,
        "extras": {
            "disable_groups": True
        },
        "evidence": symptoms
    }
    parser = ConfigParser()
    parser.read('configurations.ini')

    app_id = parser.get('auth', 'app_id')
    app_key = parser.get('auth', 'app_key')

    header = {
        'Content-Type': 'application/json',
        'App-Id': app_id,
        'App-Key': app_key
    }
    # print(f'symptoms: {symptoms}, type: {type(symptoms)}')
    # print('[*] Sending diagnosis request...')
    r = requests.post(url=url, json=body, headers=header)

    return r.text
