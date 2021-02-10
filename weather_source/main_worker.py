# -*- coding: utf-8 -*-
import datetime
import locale

from abc import ABCMeta, abstractmethod
from collections import defaultdict

from weather_source.source_url import YandexWeather, MailWeather
from weather_source.source_api import WeatherMap

from weather_source.files.models import DatabaseUpdater
from weather_source.user_represent import ImageMaker
from weather_source.files.settings import SCENARIOS_WEATHER, SOURCE_WEATHER
from weather_source.functions_subworkers import LOG


class DateError(Exception):
    def __init__(self, *args):
        self.name_error = "Неправильный ввод даты"
        self.details = args

    def __str__(self):
        return f'\n \n {self.name_error}: {self.details} \n \n'


class Worker(metaclass=ABCMeta):
    def __init__(self, source=1, city='Москва', command='push', dates=None, stat_mode=False):

        # 1 - яндекс, 2 - мэйл, 3 - weathermap_api
        self.parser_source = None
        self.bs4 = None
        self.service_source = SOURCE_WEATHER.get(source, 1)
        self.data_weather = defaultdict(dict)
        self.date_range = self._expand_date_range(dates)

        self.services_dict = {'YandexWeather': YandexWeather,
                              'MailWeather': MailWeather,
                              'WeatherMap': WeatherMap}

        self.action = {'push': self.push_db, 'pull': self.pull_db,
                       'card': self.card, 'console': self.console}.get(command)

        self.city = city.capitalize()
        self.stat_mode = stat_mode

    def _expand_date_range(self, input_date):
        """
        разворачивание списка дат
        [2020.05.20, 2020.05.22] -> [2020.05.20, 2020.05.21, 2020.05.22]
        """
        transform_dates = [datetime.datetime.strptime(i, '%Y.%m.%d').date() for i in
                           input_date[0].split('-')] if input_date else []
        if len(transform_dates) == 2:
            d1 = transform_dates[0]
            d2 = transform_dates[1]
            delta = d2 - d1  # timedelta
            if delta.days <= 0:
                raise DateError(transform_dates)
            transform_dates.clear()
            for i in range(delta.days + 1):
                transform_dates.append(d1 + datetime.timedelta(i))
        return transform_dates

    @abstractmethod
    def get_weather(self):
        """generate source, start parse"""
        raise NotImplementedError

    @abstractmethod
    def mean_total_weather(self):
        """generate source, start parse with all services and mean calc weather"""
        raise NotImplementedError

    def push_db(self, *args, **context):
        """
        Загрузка информации о погоде в БД
        :param args: not used
        :param context: dict формата {param weather/base: value/my_working_base}
        расшифровка ключей param weather: date_weather - дата
                                          part_day - часть суток
                                          weather - dict формата {"temp": value, "weather": value}
        """
        LOG.info(f"PUSH weather in DB for {context.get('date_weather')}, {context.get('part_day')}")
        context.get('base').base_pusher(context.get('date_weather'), context.get('part_day'),
                                        context.get('weather'), self.city)

    def pull_db(self, *args, **context):
        """
        Выгрузка информации о погоде с БД
        :param args: not used
        :param context: dict формата {base: my_working_base}
        """
        LOG.info(f"PULL weather from DB for {self.date_range}")
        for city, date, part_day, weather in context.get('base').base_puller(self.date_range, self.city):
            self.data_weather[date.date()][part_day] = {'weather': weather['weather'], 'temp': weather['temp']}

    def card(self, *args, **context):
        """
        Печать открытки с информацией о погоде
        :param args: not used
        :param context: dict формата {param weather/img: value/instance класса ImageMaker}
        расшифровка ключей param weather: date_weather - дата
                                          part_day - часть суток
                                          weather - dict формата {"temp": value, "weather": value}
        """

        LOG.info(f"add in CARD weather for {context.get('date_weather')}-{context.get('part_day')}")
        context.get('img').run(context.get('date_weather'), context.get('part_day'), context.get('weather'))

    def console(self, *args, **context):
        """
        Вывод информации о погоде на консоль
        :param args: not used
        :param context: dict формата {param weather: value}
        расшифровка ключей param weather: date_weather - дата
                                          part_day - часть суток
                                          weather - dict формата {"temp": value, "weather": value}
        """
        LOG.info(f"return weather in CONSOLE for {context.get('date_weather')}, {context.get('part_day')}")
        self.user_console_print(context.get('date_weather'), context.get('part_day'), context.get('weather'))

    def base_run(self, name_db='DEBUG'):
        """main method"""
        base = DatabaseUpdater()
        base.base_init(name_db)
        SCENARIOS_WEATHER['dates'] = self.date_range
        SCENARIOS_WEATHER['city'] = self.city.lower()

        if self.action.__name__ == 'push_db':
            self.give_base()
        else:
            self.take_from_base(base)

        self.command_for_base(base,
                              sorted_date_weather=sorted(self.data_weather.items(), key=lambda x: x[0]),
                              img=self.work_additionally())

    def command_for_base(self, base, sorted_date_weather, img=None):
        """
        Итоговые манипуляции с данными БД. action IN []
        :param base: рабочая БД
        :param sorted_date_weather: отсортированный dict с данными о погоде
        :param img: шаблон открытки (при command = card)
        """
        for date_weather, part_day, weather in self._fork_data(sorted_date_weather):
            self.action(base=base, date_weather=date_weather, part_day=part_day, weather=weather, img=img)
        else:
            base.close() if base else print(f'bye bye')

    def take_from_base(self, base):
        """
        Выгрузка инфо о погоде из БД, сохраняем в data_weather
        :param base: рабочая БД
        """
        self.pull_db(base=base)

    def give_base(self):
        """
        Загрузка согласно установленным параметрам данных о погоде в БД
        """
        self.get_weather() if not self.stat_mode else self.mean_total_weather()

    def work_additionally(self):
        """
        :return: instance класса отрисовки открытки
        В будущем, возможно, появится класс GifMaker
        """
        return ImageMaker(self.city) if self.action.__name__ == 'card' else None

    def _fork_data(self, data_dict):
        """
        проход по словарю с данными
        :param data_dict: словарь с собранными данными о погоде
        """
        for date_weather, weather_dict in data_dict:
            for part_day, weather in weather_dict.items():
                yield date_weather, part_day, weather

    def user_console_print(self, date_weather, part_day, weather):
        """
        Установка формата печати на консоль
        :param date_weather: дата
        :param part_day: часть суток
        :param weather: dict формата {"temp": value, "weather": value}
        """
        locale.setlocale(locale.LC_ALL, '')
        if isinstance(self.date_range, list):
            if len(self.date_range) == 1:
                if date_weather <= self.date_range[0]:
                    self._text_on_console(date_weather, part_day, weather)
            else:
                if date_weather in self.date_range:
                    self._text_on_console(date_weather, part_day, weather)

    def _text_on_console(self, date_weather, part_day, weather):
        """
        Печать текста
        :param date_weather: дата
        :param part_day: часть суток
        :param weather: dict формата {"temp": value, "weather": value}
        """
        print(f' {date_weather}, {part_day}: {weather["temp"]}, {weather["weather"]} ')

    def __len__(self):
        return (self.date_range[1] - self.date_range[0]).days if self.date_range[1] != self.date_range[0] else 1
