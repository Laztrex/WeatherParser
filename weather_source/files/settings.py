# -*- coding: utf-8 -*-
import json
import logging
import os

LOG = logging.getLogger('weather')

SCENARIOS_WEATHER = {
    "city": "воронеж",
    "dates": None,
    "stat_mode": False,
    "params": {
        "part_day": {
            'ru': ['Утро', 'День', 'Вечер', 'Ночь'],
            'en': ['Morning', 'Day', 'Evening', 'Night']
        }
    },
    "appid_WeatherMap": "2e86a4b6e54c2f514e411e63e023968c",
    "dangerous_weather": {
        "солнечно": 0.01,
        "ясно": 0.05,
        "туман": 0.08,
        "дымка": 0.08,
        "малооблачно": 0.09,
        "пасмурно": 0.1,
        'небольшая облачность': 0.1,
        "переменная облачность": 0.11,
        "облачно с прояснениями": 0.12,
        "облачно": 0.15,
        "облачность": 0.15,
        "морось": 0.2,
        "небольшой дождь": 0.25,
        "дождь": 0.3,
        "ливень": 0.35,
        "ливневый дождь": 0.35,
        "снег": 0.4,
        "гроза": 0.5,
        "шторм": 0.7,
        "ураган": 0.8,
        "торнадо": 0.9,
    },
    "main_weather_color_map":
        {
            'sunny_strong': 0,  # солнечно стандарт cv2.COLORMAP_AUTUMN
            'sunny_soft': 7,  # cv2.COLORMAP_SPRING солнечно альтернативный
            'clear': 6,  # cv2.COLORMAP_SUMMER - ясно
            'gray': 1,  # cv2.COLORMAP_BONE - пасмурная погода
            'cloudy': 10,  # cv2.COLORMAP_PINK - облачно
            'haze': 17,  # cv2.COLORMAP_CIVIDIS - дымка=туман
            'small_rain': 12,  # cv2.COLORMAP_PARULA - небольшой дождь
            'rain': 3,  # cv2.COLORMAP_WINTER - дождь
            'shower': 5,  # cv2.COLORMAP_OCEAN - ливень
            'storm': 18,  # cv2.COLORMAP_TWILIGHT - дождь
            'snow': 8,  # cv2.COLORMAP_COOL - снег
            'tornado': 15,  # cv2.COLORMAP_PLASMA
        },
    "icon_weather":
    # """Copyright (c) 2013, KickstandApps (kickstandapps.com).
    # This Font Software is licensed under the SIL Open Font License, Version 1.1.
    # This license is copied below, and is also available with a FAQ at: http://scripts.sil.org/OFL"""
        {
            'sunny_strong': 'Sun.jpg',
            'sunny_soft': 'Sunrise.jpg',
            'clear': 'Sun-thin.jpg',
            'gray': 'Cloud.jpg',
            'cloudy': 'Cloud-thin.jpg',
            'haze': 'Haze.jpg',
            'fog': 'Fog.jpg',
            'rain': 'Rain.jpg',
            'shower': 'Hail.jpg',
            'storm': 'Storm.jpg',
            'snow': 'Snow.jpg',
            'tornado': 'Tornado.jpg',
            'default': 'Moon.jpg',
        },
    "part_day_icon":
        {
            'Утро': 'morning.png',
            'День': 'day.png',
            'Вечер': 'evening.png',
            'Ночь': 'night.png'
        },
    "degree_icon": 'degree.jpg',

    "PATH_TEMP": os.path.normpath(os.path.dirname(__file__) + '/probe.jpg'),
    "PATH_ICON": os.path.normpath(os.path.dirname(__file__) + '/icons/{mode}/{icon}'),
    "TEXT_XY": {"Хроника": ((330, 360), (150, 150), (440, 470), (150, 150)),
                "В мире": ((330, 360), (60, 60), (440, 470), (60, 60))},  # x1, y1, x2, y2
    "TEXT_TEMP": ((60, 40), 16, 0.8, (0, 0, 0), 2, 16),
    "TEXT_WEATHER": ((140, 25), 3, 0.4, (0, 0, 0), 0, 16),
    "TEXT_DATE": ((305, 20), 3, 0.4, (0, 0, 0), 1, 16),
    "TEXT_INFO": ((300, {'Хроника': 180, 'В мире': 80}), 3, 0.4, (0, 0, 0), 1, 16),
    "TEXT_CITY": ((305, 45), 3, 0.4, (0, 0, 0), 1, 16),
    "ICON_WEATHER": {'Утро': ((5, 65), (0, 280)), "День": ((68, 128), (0, 280)),
                     'Вечер': ((130, 190), (0, 280)), "Ночь": ((193, 253), (0, 280))},
    "ICON_PART_DAYS": {'Утро': ((10, 60), (5, 55)), "День": ((73, 123), (5, 55)),
                       'Вечер': ((135, 185), (5, 55)), "Ночь": ((198, 248), (5, 55))},
    "ICON_DEGREE": {'x1': 130, 'x2': 115, 'y1': 30, 'y2': 15},
}

print(os.path.normpath(os.path.dirname(__file__)))


class WeatherDungerous:
    """для сортировки по вредности погоды"""

    def __init__(self, name, x):
        self.name = name
        self.dangerous = x

    def __repr__(self):
        return self.name

    @staticmethod
    def byDangerous_key(wea):
        return wea.dangerous


def analyze_weather(list_weathers):
    """
    :param list_weathers: список погоды для сортировки по вредности
    :return: самая вредная погода
    """
    weather_indexes = []
    for index, weather in enumerate(list_weathers):
        weather = WeatherDungerous(weather, SCENARIOS_WEATHER['dangerous_weather'].get(weather, 0.05))
        weather_indexes.append(weather)

    sorted_result = sorted(weather_indexes, key=WeatherDungerous.byDangerous_key, reverse=True)
    return str(sorted_result[0]).capitalize()


def return_weather_colored_and_logo(weather):
    """
    для модуля "user_represent", рисование открытки.
    :param weather: погода для анализа
    :return: цветовая гамма для заполнения открытки, иконка погоды
    """
    koeff = SCENARIOS_WEATHER["dangerous_weather"].get(weather, 0.99)
    if koeff <= 0.05:
        return SCENARIOS_WEATHER["main_weather_color_map"]["sunny_strong"], \
               SCENARIOS_WEATHER["icon_weather"]["sunny_strong"]
    elif koeff == 0.05:
        return SCENARIOS_WEATHER["main_weather_color_map"]["clear"], \
               SCENARIOS_WEATHER["icon_weather"]["clear"]
    elif koeff == 0.08:
        return SCENARIOS_WEATHER["main_weather_color_map"]["haze"], \
               SCENARIOS_WEATHER["icon_weather"]["fog"]
    elif 0.08 < koeff <= 0.12:
        return SCENARIOS_WEATHER["main_weather_color_map"]["haze"], \
               SCENARIOS_WEATHER["icon_weather"]["haze"]
    elif koeff == 0.15:
        return SCENARIOS_WEATHER["main_weather_color_map"]["gray"], \
               SCENARIOS_WEATHER["icon_weather"]["gray"]
    elif 0.19 < koeff <= 0.3:
        return SCENARIOS_WEATHER["main_weather_color_map"]["rain"], \
               SCENARIOS_WEATHER["icon_weather"]["rain"]
    elif koeff == 0.35:
        return SCENARIOS_WEATHER["main_weather_color_map"]["shower"], \
               SCENARIOS_WEATHER["icon_weather"]["shower"]
    elif koeff == 0.4:
        return SCENARIOS_WEATHER["main_weather_color_map"]["snow"], \
               SCENARIOS_WEATHER["icon_weather"]["snow"]
    elif 0.5 <= koeff < 0.9:
        return SCENARIOS_WEATHER["main_weather_color_map"]["storm"], \
               SCENARIOS_WEATHER["icon_weather"]["storm"]
    elif koeff == 0.9:
        return SCENARIOS_WEATHER["main_weather_color_map"]["tornado"], \
               SCENARIOS_WEATHER["icon_weather"]["tornado"]
    else:
        return SCENARIOS_WEATHER["main_weather_color_map"][
                   "sunny_soft"], SCENARIOS_WEATHER["icon_weather"][
                   "default"]  # пока такой, потом надо придумать нейтральный


def city_read(mode):
    """проверка, сущ. ли в файле название/id города для определенного источника погоды"""
    with open(os.path.normpath(os.path.dirname(__file__) + f'/city.json'), "r", encoding='utf-8') as read_file:
        loaded_json_file = json.load(read_file)
        try:
            return loaded_json_file[SCENARIOS_WEATHER['city']][mode]
        except KeyError as exc:
            return False


def city_write(mode, city):
    """если в файле название/id города для определенного источника погоды отсутствует - запись"""
    with open(os.path.normpath(os.path.dirname(__file__) + f'/city.json'), "r", encoding='utf-8') as write_file:
        b = json.load(write_file)
        if SCENARIOS_WEATHER['city'] not in b:
            b.update({SCENARIOS_WEATHER['city']: {}})
        b[SCENARIOS_WEATHER['city']].update({mode: city})
    with open(os.path.normpath(os.path.dirname(__file__) + f'/city.json'), "w", encoding='utf-8') as write_file:
        json.dump(b, write_file, indent=2, ensure_ascii=False)


def configure_logging():
    LOG.setLevel(logging.INFO)
    file_log = logging.FileHandler('weather.log', encoding='utf-8')
    file_log.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    LOG.addHandler(file_log)
