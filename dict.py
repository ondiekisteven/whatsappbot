try:
    from pprint import pprint
    from PyDictionary import PyDictionary
    from googletrans import Translator
except Exception as e:
    print('Modules missing {}'.format(e))

dictionary = PyDictionary()
translator = Translator()

language_code = [
    {
        'en': 'English',
        'hi': 'Hindi',
        'es': 'Spanish',
        'fr': 'French',
        'ja': 'Japanese',
        'ru': 'Russian',
        'de': 'German',
        'it': 'Italian',
        'ko': 'Korean',
        'pt-BR': 'Brazilian Portuguese',
        'zh-CN': 'Chinese (Simplified)',
        'ar': 'Arabic',
        'tr': 'Turkish'
    }
]


def meaningSynonym(word):
    #word = input('Enter a word or words separated by space to get meaning: ')
    many = word.split()
    res = ''
    for i in many:
        res += f'MEANING: {dictionary.meaning(i)}\n\n\n'
        res += f'SYNONYM: {dictionary.synonym(i)}\n\n'

    return res


def meanings(words):
    #words = input('Enter words separated by space if more than one')
    many = words.split()
    means = PyDictionary(many)
    print(means.printMeanings())


def translateWord(word):
    #word = input('Enter a word to translate: ')
    #pprint(language_code)
    #code = input('Chose code to translate to e.g en')
    return dictionary.translate(word, 'fr')


def transFr(words):
    #words = input('Enter words separated by space if more than one : ')
    #print('Chose a code below')
    #pprint(language_code)
    #code = input('Chose code to translate to e.g en: ')
    many = words.split()
    #trans = PyDictionary(many)
    
    
    print('Translating') 
    return translator.translate(many, dest='fr'))


