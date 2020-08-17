import requests
from bs4 import BeautifulSoup


def parse_current_news():
    """парсинг новостей в день создания открытки"""
    response = requests.get(f'https://yandex.ru/')
    bs = BeautifulSoup(response.text, features='html.parser')
    return [[i.text for i in el.contents[0]] for el in
            bs.find_all('div', {'class': 'news__panel mix-tabber-slide2__panel'})][0]


def parse_chronicle_in_date(date):
    """Парсинг исторических событий в дату"""
    response = requests.get(f'https://www.calend.ru/events/{date.month}-{date.day}/')
    bs = BeautifulSoup(response.text, features='html.parser')
    return [(el.contents[1].text, el.contents[3].text, el.contents[5].next.attrs['href']) for el in
            bs.find_all('div', {'class': 'caption'})]


def parse_flag_city(city, lang='ru'):
    """парсинг флага города"""
    # lang = 'ru' if city[1] in SCENARIOS_WEATHER['ru'] else 'en'
    url = f'https://{lang}.wikipedia.org/wiki/{city}'
    resp = requests.get(url)
    bs = BeautifulSoup(resp.text, features='html.parser')
    right_table = [lm.contents[0].attrs['src'] for lm in bs.find_all('a', class_='image')]
    img_url = right_table[1]
    resp_img = requests.get('https:' + img_url, stream=True).raw
    return resp_img
