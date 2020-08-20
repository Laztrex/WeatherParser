# -*- coding: utf-8 -*-
import datetime
import sys
import requests

from bs4 import BeautifulSoup
from collections import namedtuple

from weather_source.main_worker import Worker
from weather_source.files.settings import SCENARIOS_WEATHER
from weather_source.stat_decorator import parse_func
from weather_source._functions_subworkers import LOG


class DateError(Exception):
    def __init__(self, *args):
        self.name_error = "Неправильный ввод даты"
        self.details = args

    def __str__(self):
        return f'\n \n {self.name_error}: {self.details} \n \n'


class WeatherMaker(Worker):
    """
    Main parser weather
    Use python 3.7.5
    """

    def get_weather(self):
        """generate source, start parse"""
        if not self.markers[0]:
            self._parse_entered_dates()
            if self.source_weather == 'яндекс':
                self.bs4 = self.analyze(self.generate_source())
                self.get_info_from_url()
            else:
                self.get_info_from_url(flag=True)

    def analyze(self, source):
        """
        сбор инфы о погоде
        :param source: источник погоды
        """
        response = requests.get(source)
        return BeautifulSoup(response.text, features='html.parser')

    def get_info_from_url(self, flag=False):
        """
        перегруппировка погодных данных
        :param flag: True - если источник mail или API
        """
        list_date = self.source_modified.dates_weather(self.bs4) if not flag else self.date_range.copy()
        list_temp = self.grouper(self._get_temp_from_url(self.bs4), 4) if not flag else []
        list_weather = self.grouper(self._get_weather_from_url(self.bs4), 4) if not flag else []
        Record = namedtuple('Record', 'date temp weather')
        if flag:
            self.enable_workaround(list_date, list_temp, list_weather)
        self.get_weather_dict([Record(*t) for t in zip(*(list_date, list_temp, list_weather)) if t[0] in self.date_range])
        if self.date_range and not self.stat_mode:
            LOG.info('Остались необработанные даты')
            if self.source_weather == 'api':
                self.source_weather = 'mail'
            self.get_info_from_url(flag=True)

    @parse_func
    def get_weather_dict(self, total_weather_info):
        """
        добавляем в общий словарь
        :param total_weather_info: сгруппированные собранные данные
        """
        for info_weather in total_weather_info:
            dates_for_weather = self._select_dates(info_weather.date)
            if dates_for_weather:
                self.data_weather[dates_for_weather] = \
                    {part_day: {'temp': data_weather[0], 'weather': data_weather[1].lower()} for part_day, data_weather
                     in
                     zip(SCENARIOS_WEATHER["params"]["part_day"]['ru'], zip(info_weather.temp, info_weather.weather))}

    def enable_workaround(self, list_date, list_temp, list_weather):
        """
        Запускается, если остались необработанные данные
        :param list_date: обновляющийся список дат
        :param list_temp: обновляющийся список температур
        :param list_weather: обновляющийся список погод
        :return: в режиме "API"
        """
        if self.source_weather == 'api':
            self.generate_source(self, self.city)
            try:
                self.source_modified.run_api(list_date, list_temp, list_weather)
            except Exception as exc:
                sys.exit(exc)
            return
        for on_date in list_date:
            self.source_weather = 'мэйл'
            self.bs4 = self.analyze(self.generate_source(on_date))
            list_temp.append(self.source_modified.temp_weather(bs=self.bs4))
            list_weather.append(self.source_modified.weather(self.bs4))

    def _select_dates(self, my_date):
        """
        :param my_date: дата для проверки на введенный диапазон. Нужно, так как с yandex и API
        парситься целым скопом на 10 и 5 дней
        :return: my_date - если принадлежит пользовательскому диапазону дат, False - нет
        """
        if my_date in self.date_range:
            self.date_range.remove(my_date) if not self.stat_mode else None
            return my_date
        elif my_date.month == 1:
            my_date = my_date.replace(year=my_date.year + 1)
            return self._select_dates(my_date)
        return False

    def _parse_entered_dates(self):
        """
        разворачивание списка дат
        [2020.05.20, 2020.05.22] -> [2020.05.20, 2020.05.21, 2020.05.22]
        """
        if len(self.date_range) == 2:
            d1 = self.date_range[0]
            d2 = self.date_range[1]
            delta = d2 - d1  # timedelta
            if delta.days <= 0:
                raise DateError(self.date_range)
            self.date_range.clear()
            for i in range(delta.days + 1):
                self.date_range.append(d1 + datetime.timedelta(i))
        else:
            pass

    def generate_source(self, *kwargs):
        """
        :param kwargs: параметры для генерируемого источника данных
        :return: ссылка для парсинга от выбранного источника
        """
        LOG.info(f'Запущен сервис {self.service[self.source_weather].__name__}')
        self.source_modified = self.service[self.source_weather](*kwargs)
        LOG.info(f"Копошение в {self.source_modified}")
        return self.source_modified

    def _get_temp_from_url(self, bs):
        """добавляем температуру"""
        return self.source_modified.temp_weather(bs)

    def _get_weather_from_url(self, bs):
        """добавляем погоду"""
        return self.source_modified.weather(bs)

    @staticmethod
    def grouper(input_data, n):
        args = [iter(input_data)] * n
        return zip(*args)

    def mean_total_weather(self):
        """среднее из трех источников"""
        for source in self.service.keys():
            print(f'ПЕРЕШЛИ ЧЕРЕЗ {source}')
            self.source_weather = source
            self.get_weather()
        self.date_range.clear()
