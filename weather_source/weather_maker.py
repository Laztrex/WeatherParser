# -*- coding: utf-8 -*-
import sys
import requests

from bs4 import BeautifulSoup
from collections import namedtuple

try:
    from weather_source.files.settings import SCENARIOS_WEATHER, SOURCE_WEATHER
except ImportError:
    exit('Do cp weather_source/files/settings.py.default '
         'weather_source/files/settings.py and set API WeatherOpenMap token!')

from weather_source.main_worker import Worker
from weather_source.stat_decorator import parse_func
from weather_source.functions_subworkers import LOG


class WeatherMaker(Worker):
    """
    Main parser weather
    Use python 3.7.5
    """

    # тут происходят какие-то макароны. Давайте распутывать

    def get_weather(self):
        """generate source, start parse"""
        flag_all_processed_dates = False
        while not flag_all_processed_dates:
            if self.service_source == 'YandexWeather':
                self.bs4 = self.response_from_source(self.generate_source())
                flag_all_processed_dates = self.get_info_from_url()
            else:
                flag_all_processed_dates = self.get_info_from_url(not_default_source=True)

    def response_from_source(self, source):
        """
        сбор инфы о погоде
        :param source: источник погоды
        """
        response = requests.get(source)
        return BeautifulSoup(response.text, features='html.parser')

    def init_lists_from_weathers_data(self, not_default_source):
        """
        Старт парсинга для 'яндекс' или инициализация для других источников
        :param not_default_source:
        :return: см. docstring метода <<_compress_collected_data>>
        """
        return self.parser_source.dates_weather(self.bs4) if not not_default_source else self.date_range.copy(), \
               self.grouper(self._get_temp_from_url(self.bs4), 4) if not not_default_source else [], \
               self.grouper(self._get_weather_from_url(self.bs4), 4) if not not_default_source else []

    def get_info_from_url(self, not_default_source=False):
        """
        создания списков для объединения набора погодных данных
        :param not_default_source: True - если источник mail или API, иначе - яндекс
        """
        list_date, list_temp, list_weather = self.init_lists_from_weathers_data(not_default_source)

        if not_default_source:
            self.enable_workaround(list_date, list_temp, list_weather)

        compress_data_weather = self._compress_collected_data(list_date, list_temp, list_weather)
        self.get_weather_dict(compress_data_weather)

        if self.date_range and not self.stat_mode:
            LOG.info('Остались необработанные даты')
            self.service_source = SOURCE_WEATHER.get(2)
            return False
        return True

    def _compress_collected_data(self, list_date, list_temp, list_weather):
        """
        Сжатие/группировка массивов погодных данных в nametuple-сущности
        :param list_date: список из 10-ти распарсенных дат в яндексе или copy self.data_range
        :param list_temp: яндекс: zip распарсенных температур и сгруппированных по 4 из <<grouper(input_data, n)>>
                          иначе: список из [[10]] * 4 распарсенных температур (по 4 на день)
        :param list_weather: аналогично как и для list_temp для погодных характеристик
        :return: gen expression of nametuples
        """
        Record = namedtuple('Record', 'date temp weather')

        return [Record(*date_temp_weather) for date_temp_weather in zip(*(list_date, list_temp, list_weather))
                if date_temp_weather[0] in self.date_range]

    @parse_func
    def get_weather_dict(self, total_weather_info):
        """
        добавляем в итоговый словарь
        :param total_weather_info: type - gen expression with nametuples. from method <<_compress_collected_data>>
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
        Запускается, если остались необработанные даты

        :param list_date: обновляющийся список дат
        :param list_temp: обновляющийся список температур
        :param list_weather: обновляющийся список погод
        """
        if self.service_source == 'WeatherMap':
            self.generate_source(self, self.city)
            try:
                self.parser_source.run_api(list_date, list_temp, list_weather)
            except Exception as exc:
                print(exc)
            return
        for on_date in list_date:
            self.service_source = 'MailWeather'
            self.bs4 = self.response_from_source(self.generate_source(on_date))
            list_temp.append(self.parser_source.temp_weather(bs=self.bs4))
            list_weather.append(self.parser_source.weather(self.bs4))

    def _check_date_in_date_range(self, my_date):
        if my_date in self.date_range:
            self.date_range.remove(my_date) if not self.stat_mode else None
            return my_date

    def _set_next_year(self, my_date):
        my_date = my_date.replace(year=my_date.year + 1)
        return my_date

    def _select_dates(self, my_date):
        """
        :param my_date: дата для проверки на введенный диапазон. Нужно, так как с yandex и API
        парситься целым скопом на 10 и 5 дней
        :return: my_date - если принадлежит пользовательскому диапазону дат, False - нет
        """
        result_checked = self._check_date_in_date_range(my_date)
        if result_checked:
            return result_checked
        else:
            if my_date.month == 1:
                result_checked_next_year = self._check_date_in_date_range(self._set_next_year(my_date))
                return result_checked_next_year if result_checked_next_year else False

    def generate_source(self, *kwargs):
        """
        :param kwargs: параметры для генерируемого источника данных
        :return: ссылка для парсинга от выбранного источника
        """
        LOG.info(f'Запущен сервис {self.service_source}')
        self.parser_source = self.services_dict[self.service_source](*kwargs)
        LOG.info(f"Копошение в {self.parser_source}")
        return self.parser_source

    def _get_temp_from_url(self, bs):
        """добавляем температуру"""
        return self.parser_source.temp_weather(bs)

    def _get_weather_from_url(self, bs):
        """добавляем погоду"""
        return self.parser_source.weather(bs)

    @staticmethod
    def grouper(input_data, n):
        args = [iter(input_data)] * n
        return zip(*args)

    def mean_total_weather(self):
        """среднее из трех источников"""
        for source in SOURCE_WEATHER.values():
            print(f'ПЕРЕШЛИ ЧЕРЕЗ {source}')
            self.service_source = source
            self.get_weather()
        self.date_range.clear()
