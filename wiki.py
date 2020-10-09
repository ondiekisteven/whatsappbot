import wikipedia 
from pywikihow import search_wikihow, HowTo, RandomHowTo


# ------------------------------------ WIKIPEDIA ------------------------------------------
def page(title):
    page = wikipedia.page(title)
    return {
        "t": page.title,
        "d": page.content
    }

# ------------------------------------- WIKI-HOW -------------------------------------------
def parse_search_howto(item: HowTo):
    item = item.as_dict()
    search_title = item['title']
    search_url = item['url']
    search_steps = ''

    for step in item['steps']:
        step_number = step['number']
        step_summary = step['summary']
        step_description = step['description']
        search_steps += f'*{step_number}. {step_summary}*\n\n{step_description}\n\n'

    return f'*How to {search_title}*\n*{search_url}*\n\n*STEPS:*\n{search_steps}'


def search_howto_index(term: str, pos: int):
    how_tos = search_wikihow(term)
    return parse_search_howto(how_tos[pos])


def search_howto(term: str):
    how_tos = search_wikihow(term, max_results=10)
    res = '*Select the article you want to view.*\n'
    for index, item in enumerate(how_tos):
        res += f'{index + 1} - {item}\n\n'
    return {
        'articles': res,
        'size': len(how_tos)
    }


def random_how_to():
    r_h_t = RandomHowTo()
    return parse_search_howto(r_h_t)

