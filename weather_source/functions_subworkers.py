import json
import logging

from weather_source.files.settings import SCENARIOS_WEATHER


LOG = logging.getLogger('weather')


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
    with open('files/city.json', "r", encoding='utf-8') as read_file:
        loaded_json_file = json.load(read_file)
        try:
            return loaded_json_file[SCENARIOS_WEATHER['city']][mode]
        except KeyError as exc:
            return False


def city_write(mode, city):
    """если в файле название/id города для определенного источника погоды отсутствует - запись"""
    with open('files/city.json', "r", encoding='utf-8') as write_file:
        b = json.load(write_file)
        if SCENARIOS_WEATHER['city'] not in b:
            b.update({SCENARIOS_WEATHER['city']: {}})
        b[SCENARIOS_WEATHER['city']].update({mode: city})
    with open('files/city.json', "w", encoding='utf-8') as write_file:
        json.dump(b, write_file, indent=2, ensure_ascii=False)


def configure_logging():
    LOG.setLevel(logging.INFO)
    file_log = logging.FileHandler('weather.log', encoding='utf-8')
    file_log.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    LOG.addHandler(file_log)
