# -*- coding: utf-8 -*-
import datetime
import locale
import requests

from abc import ABCMeta, abstractmethod
from termcolor import cprint

from weather_source.source_url import MailWeather, FindCityError
from weather_source.functions_subworkers import analyze_weather, LOG
from weather_source.files.settings import APPID_WeatherOpenMap, SCENARIOS_WEATHER


class APIWeatherError(Exception):
    def __init__(self, *args):
        self.name_error = "Exception Error (OpenWeatherMap)"
        self.details = args

    def __str__(self):
        return f'\n \n {self.name_error}: {self.details} \n \n'


class AppIdError(Exception):
    def __init__(self, *args):
        self.name_error = "App Id API Error (OpenWeatherMap)"
        self.details = args

    def __str__(self):
        return f'\n \n {self.name_error}: ' \
               f'Проверьте ваш id в "APPID_WeatherOpenMap" - /weather_source/files/settings'


class BaseWeather(metaclass=ABCMeta):
    """
    Работа с API OpenWeatherMap
    """
    def __init__(self, source, city):
        self.appid = APPID_WeatherOpenMap
        self.s_city = f'{city},RU'
        self.city_id = None
        self.main_worker = source
        self.first_half_part, self.second_half_part = [0] * 4, [0] * 4
        self.curr_date = datetime.date.today()

    def _check_city(self):
        """поиск id города"""
        try:
            res = requests.get("http://api.openweathermap.org/data/2.5/find",
                               params={'q': self.s_city, 'type': 'like', 'units': 'metric', 'APPID': self.appid})
            if res.status_code == 200:
                data = res.json()
                self.city_id = data['list'][0]['id']
        except Exception as e:
            raise FindCityError(e)

    def run_api(self, list_date, list_temps, list_weather):
        """
        старт получения данных, определение недоступных для API дат
        :param list_date: обновляемый список дат
        :param list_temps: обновляемый список температур
        :param list_weather: обновляемый список погод
        """
        self._check_city()
        missing_dates = [i for num, i in
                         enumerate(list_date) if i < self.curr_date or
                         i - self.curr_date > datetime.timedelta(days=5)]
        if missing_dates:
            LOG.warning(f"Даты {missing_dates} не могут быть обработаны API")
            cprint(f'WARNING! Даты {missing_dates} недоступны для API. \n'
                   'Перезапустите программу с appid.', color='yellow')
            cprint('будет подключён mail.ru...', color='cyan')
            [list_date.remove(i) for i in missing_dates]

        self._get_weathers(list_date, list_temps, list_weather)

    @staticmethod
    def string_mod(temp):
        if temp > 0:
            return '+' + str(temp) + '°'
        elif temp < 0:
            return str(temp) + '°'
        else:
            return str(temp)

    def _get_weathers(self, list_date, list_temps, list_weather):
        """
        парсер погоды с выданного генератором json;
        если даты нет в списке - пропускается;
        значения приходят только на 5 дней;
        предлагается обратиться в mail.ru за будущими/оставшимися прошлыми датами
        """
        weather_in_day = []
        temp_weather = []
        for num_part, weather_data in enumerate(self.weather_from_api()):
            if weather_data[0].date() not in list_date:
                continue  # переправить на сравнение с текущей датой
            temp_weather.append(weather_data[2].lower())
            returned = self._method_for_part_days(weather_data)
            if returned:
                weather_in_day.insert(returned - 1, analyze_weather(temp_weather))
                temp_weather.clear()
            if weather_data[0].time() == datetime.time(hour=21, minute=00):
                LOG.info('Получили с API пакет информации. Обработка...')
                list_temps.append(
                    tuple(
                        map(lambda x: self.string_mod(sum(x[1]) // 2)
                        if x[1][0] and x[1][1] else self._analyze_parts(x, weather_data[0].date(), weather_in_day),
                            enumerate(zip(self.first_half_part, self.second_half_part)))
                    )
                )
                self.first_half_part = [0] * 4
                self.second_half_part = [0] * 4
                list_weather.append(tuple(weather_in_day))
                weather_in_day.clear()

    def _analyze_parts(self, analyze_parts, analyze_date, weather_in_day):
        """
        анализатор погоды на текущую дату с api;
        если не хватает погоды части суток - обращение к mail
        :param analyze_parts: tuple, (idx, (temp1, temp2)) - где temp1 и temp2 погода с api для части суток.
                              Часть суток (6 часов) состоит из двух значений (по 3 часа). Если 1 или 2 значение -
                              остается, если ни одного - обращение к мэйл за значением для части суток.
        :param analyze_date: datetime.date
        :param weather_in_day: list. Содержит погоду на день. Вставка погоды части суток по индексу
        """
        if sum(analyze_parts[1]) == 0:
            LOG.info(f'Погоду недостающей части суток берём с mail.ru...')
            mail_extend = MailWeather(dates=analyze_date)
            bs = self.main_worker.analyze(mail_extend)
            mail_source = mail_extend.weather(bs)[analyze_parts[0]]
            weather_in_day.insert(analyze_parts[0], mail_source)
            mail_source = mail_extend.temp_weather(bs)[
                analyze_parts[0]]
            return mail_source
        return self.string_mod(sum(analyze_parts[1]))

    def _method_for_part_days(self, analyze_data):
        """
        метод для вычисления температуры на конкретную часть дня;
        складывается погода с 2-мя значениями (интервал 3 часа) -> для определения средней за часть суток;
        :param analyze_data: tuple (date:datetime, temp:str, weather:str (not used))
        :return: часть суток (для вставки погоды в определенную позицию списка: утро/день/вечер/ночь - 1/2/3/4)
        """
        if analyze_data[0].time() == datetime.time(hour=6, minute=00):
            self.first_half_part[0] += int(analyze_data[1])
        if analyze_data[0].time() == datetime.time(hour=9, minute=00):
            self.second_half_part[0] += int(analyze_data[1])
            return 1
        if analyze_data[0].time() == datetime.time(hour=12, minute=00):
            self.first_half_part[1] += int(analyze_data[1])
        if analyze_data[0].time() == datetime.time(hour=15, minute=00):
            self.second_half_part[1] += int(analyze_data[1])
            return 2
        if analyze_data[0].time() == datetime.time(hour=18, minute=00):
            self.first_half_part[2] += int(analyze_data[1])
        if analyze_data[0].time() == datetime.time(hour=21, minute=00):
            self.second_half_part[2] += int(analyze_data[1])
            return 3
        if analyze_data[0].time() == datetime.time(hour=00, minute=00):
            self.first_half_part[3] += int(analyze_data[1])
        if analyze_data[0].time() == datetime.time(hour=3, minute=00):
            self.second_half_part[3] += int(analyze_data[1])
            return 4

    @abstractmethod
    def weather_from_api(self):
        pass

    def current_weather(self):
        pass


class WeatherMap(BaseWeather):

    def current_weather(self):
        """выдача текущей погоды"""
        locale.setlocale(locale.LC_ALL, '')
        if self.appid is None:
            raise AppIdError
        try:
            res = requests.get("http://api.openweathermap.org/data/2.5/weather",
                               params={'id': self.city_id, 'units': 'metric', 'lang': 'ru', 'APPID': self.appid})
            data = res.json()
            return {"weather:": data['weather'][0]['description'], 'temp': data['main']['temp']}
        except Exception as e:
            raise APIWeatherError(e)

    def weather_from_api(self):
        """выдача погоды за 5 дней"""
        locale.setlocale(locale.LC_ALL, '')
        if not self.appid:
            raise AppIdError
        try:
            res = requests.get("http://api.openweathermap.org/data/2.5/forecast",
                               params={'id': self.city_id, 'units': 'metric', 'lang': 'ru', 'APPID': self.appid})
            data = res.json()
            if res.status_code == 200:
                for i in data['list']:
                    yield datetime.datetime.strptime(i['dt_txt'], '%Y-%m-%d %H:%M:%S'), '{0:+3.0f}'.format(
                        i['main']['temp']), i['weather'][0]['description']
                    locale.setlocale(locale.LC_ALL, '')
            else:
                raise TypeError(res.text)
        except Exception as e:
            raise APIWeatherError(e)

    def add_appid(self, my_id):
        SCENARIOS_WEATHER["appid_WeatherMap"] = my_id
        return 'DONE!'

    def __repr__(self):
        return self

    def __str__(self):
        return f'{__class__.__name__}'
