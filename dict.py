try:
    from pprint import pprint
    from PyDictionary import PyDictionary
    from googletrans import Translator
except Exception as e:
    print('Modules missing {}'.format(e))
import re

ACCEPTED_LINKS = [
    'https://auctionx.herokuapp.com/',
    'https://chat.whatsapp.com/INP90Mpbh8NHPk3SNOoAFi',
]

VERIFIED_USERS = [
    '254790670635@c.us',
    '254797000135@c.us',
    '254726422225@c.us',
    '254704661895@c.us',
]

def find_links(string):
    # findall() has been used
    # with valid conditions for urls in string
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex, string)
    return [x[0] for x in url]


dictionary = PyDictionary()
translator = Translator()

language_code = [
        'en',
        'sw',
        'hi',
        'es',
        'fr',
        'ja',
        'ru',
        'de',
        'it',
        'ko',
        'pt-BR',
        'zh-CN',
        'ar',
        'tr'
]
languages_list = [
    'English',
    'Kiswahili',
    'Hindi',
    'Spanish',
    'French',
    'Japanese',
    'Russian',
    'German',
    'Italian',
    'Korean',
    'Brazilian Portuguese',
    'Chinese (Simplified)',
    'Arabic',
    'Turkish'
]


def get_languages_as_text(languages):
    text = ''
    for index, item in enumerate(languages):
        text += f'{index + 1}. {item}\n'
    return text


def parse_meaning(result: dict):
    final_text = '\n'
    m_keys = result.keys()
    for key in m_keys:
        interim_text = f"\t*{key.upper()}*\n"
        for item in result[key]:
            interim_text += '-> ' + item + "\n"
        final_text += interim_text

    return final_text


def parse_synonyms(result: list):
    final = '\n'
    for item in result:
        final += f'-> {item}\n'
    
    return final


def meaningSynonym(word):
    word = word.split(' ')[0]
    # word = input('Enter a word or words separated by space to get meaning: ')
    res = ''
    mns = dictionary.meaning(word)
    synonyms = dictionary.synonym(word)
    res += f'MEANING: {parse_meaning(dictionary.meaning(word))}\n\n'
    res += f'SYNONYM: {parse_synonyms(dictionary.synonym(word))}\n\n'

    return res


def meanings(words):
    # words = input('Enter words separated by space if more than one')
    many = words.split()
    means = PyDictionary(many)
    print(means.printMeanings())


def translateWord(word):
    # word = input('Enter a word to translate: ')
    # pprint(language_code)
    # code = input('Chose code to translate to e.g en')
    return dictionary.translate(word, 'fr')


def transFr(words, lang='fr'):
    print(f'Translating {words} to {lang}')
    translation = translator.translate(words, dest=lang)
    final = f"{translation.origin} ({translation.src}) --> {translation.text} ({translation.dest})"
    return final

