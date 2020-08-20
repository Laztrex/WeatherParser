# -*- coding: utf-8 -*-
import os

APPID_WeatherOpenMap = '2e86a4b6e54c2f514e411e63e023968c'


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
    'ru': 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя',
    'en': 'abcdefghijklmnopqrstuvwxyz',

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
    "ICON_WEATHER": {'Утро': ((5, 65), (5, 285)), "День": ((68, 128), (5, 285)),
                     'Вечер': ((130, 190), (5, 285)), "Ночь": ((193, 253), (5, 285))},
    "ICON_PART_DAYS": {'Утро': ((10, 60), (10, 60)), "День": ((73, 123), (10, 60)),
                       'Вечер': ((135, 185), (10, 60)), "Ночь": ((198, 248), (10, 60))},
    "ICON_DEGREE": {'x1': 130, 'x2': 115, 'y1': 30, 'y2': 15},
}
