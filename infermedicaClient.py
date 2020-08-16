import infermedica_api
from json import dumps, loads
from apiHelper import parseDatabaseSymptoms
from configparser import ConfigParser
import requests


def get_instance():
    parser = ConfigParser()    # create a config parser
    parser.read('configurations.ini')  #reading configuration file

    aId = parser.get('auth', 'app_id')
    aKey = parser.get('auth', 'app_key')

    infermedica_api.configure(app_id=aId, app_key=aKey) # configure our api to authenticate requests

    api = infermedica_api.get_api()
    return api


# creating a diagnosis request object. age and sex are passed as initial arguments
def get_diagnosis(age, sex):
    myRequest = infermedica_api.Diagnosis(sex=sex, age=age)
    print("[OK] Created diagnosis object")
    return myRequest


# Making actual diagnosis request
def make_diagnosis_request(instance, diagnosis_request):
    diagnosis_request.set_extras('disable_groups', True, True)
    print(f'[OK] Created a diagnosis request object: {diagnosis_request}')
    return instance.diagnosis(diagnosis_request)


# appending all symptoms to the request object created.
def append_symptoms(request, symptoms):
    print(f'SYMPTOMS IN APPEND FUNCTION IS: {symptoms}')

    print(f'[*] Appending existing symptoms to request...')
    for symptom in symptoms:
        print(f'{symptom}')
        symptom_id = symptom["id"]
        symptom_id_choice = symptom["choice_id"]
        request.add_symptom(symptom_id, symptom_id_choice)
    print(f'[OK] DONE. Appended {len(symptoms)}')
    return request


# adding symptom to list of symptoms after user selects one choice
def add_symptom_from_choice(diagnosis_req, question_id, choice):
    print(f'[*] Adding {question_id} - {choice}')
    diagnosis_req.add_symptom(question_id, choice)
    print('[OK] Appended chosen choice to request symptoms')
    return diagnosis_req


def make_chuka_api_request(age, sex, symptoms):
    url = 'https://chuka-medics.herokuapp.com/'
    myJson = {'age': age, 'sex': sex, 'symptoms': parseDatabaseSymptoms(symptoms)}

    # print(symptoms)
    # print('[*] Sending request...')
    myJson = dumps(myJson)
    myJson = loads(myJson)
    response = requests.post(url, json=myJson)
    return response.text
