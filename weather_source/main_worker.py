# -*- coding: utf-8 -*-
import datetime
import locale

from abc import ABCMeta, abstractmethod
from collections import defaultdict

from weather_source.files.models import DatabaseUpdater
from weather_source.user_represent import ImageMaker
from weather_source.source_url import YandexWeather, MailWeather
from weather_source.source_api import WeatherMap
from weather_source.files.settings import SCENARIOS_WEATHER
from weather_source._functions_subworkers import LOG, configure_logging


class Worker(metaclass=ABCMeta):
    def __init__(self, source='яндекс', city='Москва',
                 push_base=None, pull_base=None,
                 card=None, date=None, console=None, stat=False):
        self.source_weather = source.lower() if source else None
        self.source_modified = None
        self.bs4 = None
        self.service = {'яндекс': YandexWeather, 'мэйл': MailWeather, 'api': WeatherMap}
        self.data_weather = defaultdict(dict)
        self.date_range = [datetime.datetime.strptime(i, '%Y.%m.%d').date() for i in
                           date[0].split('-')] if date else None
        self.markers = [pull_base, push_base, card, console]
        self.city = city.capitalize()
        self.stat_mode = stat

    @abstractmethod
    def get_weather(self):
        """generate source, start parse"""
        pass

    @abstractmethod
    def mean_total_weather(self):
        """generate source, start parse with all services and mean calc weather"""
        pass

    def push_db(self, base, date_weather, part_day, weather):
        LOG.info(f"PUSH weather in DB for {date_weather}, {part_day}")
        base.base_pusher(date_weather, part_day, weather, self.city)

    def pull_db(self, base):
        LOG.info(f"PULL weather from DB for {self.date_range}")
        for city, date, part_day, weather in base.base_puller(self.date_range, self.city):
            self.data_weather[date.date()][part_day] = {'weather': weather['weather'], 'temp': weather['temp']}

    def card(self, img, date_weather, part_day, weather):
        LOG.info(f"add in card weather for {date_weather}-{part_day}")
        img.run(date_weather, part_day, weather)

    def console(self, date_weather, part_day, weather):
        LOG.info(f"return weather in CONSOLE for {date_weather}, {part_day}")
        self.user_console_print(date_weather, part_day, weather)

    def base_run(self, name_db='DEBUG'):
        """main method"""
        configure_logging()
        base = DatabaseUpdater()
        base.base_init(name_db)
        img = ImageMaker(self.city) if self.markers[2] else None
        SCENARIOS_WEATHER['dates'] = self.date_range
        SCENARIOS_WEATHER['city'] = self.city.lower()
        if self.markers[1]:
            self.get_weather() if not self.stat_mode else self.mean_total_weather()
        else:
            self.pull_db(base)
        for date_weather, part_day, weather in \
                self._fork_data(sorted(self.data_weather.items(), key=lambda x: x[0])):
            if self.markers[1]:
                self.push_db(base, date_weather, part_day, weather)
            if self.markers[2]:
                self.card(img, date_weather, part_day, weather)
            if self.markers[3]:
                self.console(date_weather, part_day, weather)
        else:
            base.close() if base else print(f'bye bye')

    def _fork_data(self, data_dict):
        """
        проход по словарю с данными
        :param data_dict: словарь с собранными данными о погоде
        """
        for date_weather, weather_dict in data_dict:
            for part_day, weather in weather_dict.items():
                yield date_weather, part_day, weather

    def user_console_print(self, date_weather, part_day, weather):
        # TODO: вывести красиво
        locale.setlocale(locale.LC_ALL, '')
        if isinstance(self.date_range, list):
            if len(self.date_range) == 1:
                if date_weather <= self.date_range[0]:
                    self._text_on_console(date_weather, part_day, weather)
            else:
                if self.date_range[0] <= date_weather <= self.date_range[1]:
                    self._text_on_console(date_weather, part_day, weather)

    def _text_on_console(self, date_weather, part_day, weather):
        print(f' {date_weather}, {part_day}: {weather["temp"]}, {weather["weather"]} ')

    def __len__(self):
        return (self.date_range[1] - self.date_range[0]).days if self.date_range[1] != self.date_range[0] else 1
