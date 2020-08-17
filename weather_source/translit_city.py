# -*- coding: utf-8 -*-
import requests

from weather_source.files.settings import APPID_WeatherOpenMap


def t_crypt(city):
    """
    Поиск валидного названия города для mail.ru
    :param city: введенный город
    :return: транслитерация названия города
    """

    lower_case_letters = {u'а': u'a',
                          u'б': u'b',
                          u'в': u'v',
                          u'г': u'g',
                          u'д': u'd',
                          u'е': u'e',
                          u'ё': u'e',
                          u'ж': u'zh',
                          u'з': u'z',
                          u'и': u'i',
                          u'й': u'y',
                          u'к': u'k',
                          u'л': u'l',
                          u'м': u'm',
                          u'н': u'n',
                          u'о': u'o',
                          u'п': u'p',
                          u'р': u'r',
                          u'с': u's',
                          u'т': u't',
                          u'у': u'u',
                          u'ф': u'f',
                          u'х': u'h',
                          u'ц': u'ts',
                          u'ч': u'ch',
                          u'ш': u'sh',
                          u'щ': u'sch',
                          u'ъ': u'',
                          u'ы': u'y',
                          u'ь': u'',
                          u'э': u'e',
                          u'ю': u'yu',
                          u'я': u'ya', }

    for cyrillic_string, latin_string in lower_case_letters.items():
        city = city.replace(cyrillic_string, latin_string)
    # string = re.sub("([-\s+])", '_', string)
    return city


def t_late(city):
    """
    Поиск валидного названия города для Яндекс.Погода и API
    :param city: введенный город
    :return: валидное название города
    """
    try:
        res = requests.get("http://api.openweathermap.org/data/2.5/find",
                           params={'q': city, 'type': 'like', 'units': 'metric', 'APPID': APPID_WeatherOpenMap})
        if res.status_code == 200:
            data = res.json()
            return data['list'][0]['name'].lower().replace(' ', '-').replace('’', '')
    except Exception as e:
        print("Exception (find):", e)
        pass
