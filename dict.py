try:
    from pprint import pprint
    from PyDictionary import PyDictionary
    from googletrans import Translator
except Exception as e:
    print('Modules missing {}'.format(e))

dictionary = PyDictionary()
translator = Translator()

language_code = [
        'en',
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


def meaningSynonym(word):
    # word = input('Enter a word or words separated by space to get meaning: ')
    many = word.split()
    res = ''
    for i in many:
        res += f'MEANING: {dictionary.meaning(i)}\n\n\n'
        res += f'SYNONYM: {dictionary.synonym(i)}\n\n'

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

