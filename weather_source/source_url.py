# -*- coding: utf-8 -*-
import calendar
import datetime
import locale
import os
import re
import requests

from bs4 import BeautifulSoup

from weather_source.functions_subworkers import city_read, city_write, LOG
from weather_source.files.settings import SCENARIOS_WEATHER
from weather_source.translit_city import t_crypt, t_late


class FindCityError(Exception):
    def __init__(self, *args):
        self.name_error = "City not found!"
        self.details = args

    def __str__(self):
        return f'\n \n {self.name_error}: {self.details} \n \n'


def check_city(mode):
    """
    :param mode: t_crypt для mail.ru, t_late - для яндекса
    :return: написание города для определенного источника
    """
    answer_city = city_read(mode.__name__)
    if not answer_city:
        city_correct = mode(SCENARIOS_WEATHER['city'])
        res = requests.get(SCENARIOS_WEATHER["source_url"]["яндекс"]["weather"][:25] + city_correct + '/') \
            if mode.__name__ == 't_late' \
            else requests.get(SCENARIOS_WEATHER["source_url"]["мэйл"]["weather"][:31] + city_correct + '/')
        if res.status_code == 200:
            city_write(mode.__name__, city_correct)
            return city_correct
        else:
            if mode.__name__ == 't_late':
                city_correct = YandexWeather.find_correct_city_name()
            else:
                city_correct = MailWeather.find_correct_city_name()
            city_write(mode.__name__, city_correct)
            return city_correct
    return answer_city


class YandexWeather:
    """
    Парсер Яндекс.Погоды
    """

    def __init__(self):
        self.site = self._gen_url()

    def _gen_url(self):
        return SCENARIOS_WEATHER["source_url"]["яндекс"]["weather"].format(city=check_city(t_late))

    @staticmethod
    def find_correct_city_name():
        """поиск города, если модуль "translit_test" не справился"""
        try:
            res = requests.get(SCENARIOS_WEATHER["source_url"]["яндекс"]["search"] + SCENARIOS_WEATHER['city'])
            if res.status_code == 200:
                bs4 = BeautifulSoup(res.text, features='html.parser')
                a = bs4.find_all('li', {'class': 'place-list__item'})
                answer_res = a[0].contents[1].attrs['href'].split('?')[0].split('/pogoda/')[1]
                return answer_res
        except Exception as e:
            raise FindCityError(e)

    def dates_weather(self, bs):
        """парсится на 10 дней"""
        return [datetime.date(
            datetime.datetime.now().year,
            self._refactor_month(num_month.text[0:3]),
            int(day.text)) for day, num_month in
            zip(bs.find(attrs={'class': 'forecast-details__day'}).find_all_next('strong'),
                bs.find_all(attrs={'class': 'forecast-details__day-month'}))
        ]

    def _refactor_month(self, month):
        locale.setlocale(locale.LC_ALL, '')
        if 'мая' in month:
            return 5
        return datetime.datetime.strptime(month, "%b").month

    def _analyze_temps(self, temps):
        for sign in (("+", "+"), ("−", "-")):
            temps = temps.replace(*sign)
        only_temps = re.findall(r'[+-]?\d+', temps)
        cleared = str(round(sum(map(int, only_temps)) / 2)) if len(only_temps) > 1 else str(only_temps.pop())
        return f"{'+' if cleared[0].isdigit() else ''}{cleared}°"

    def temp_weather(self, bs):
        """аккумуляция температур"""
        LOG.info(f"Смотрим погоду через Yandex в - {SCENARIOS_WEATHER['city']}")
        return [self._analyze_temps(el.text) for el in bs.find_all('div', {'class': 'weather-table__temp'})]

    def weather(self, bs):
        """аккумуляция погод"""
        return [el.text for el in
                bs.find_all(
                    'td', {'class': 'weather-table__body-cell weather-table__body-cell_type_condition'})
                ]

    def __repr__(self):
        return self.site


class MailWeather:
    """
    Парсер с mail.ru
    """

    def __init__(self, dates=None):
        self.date_in_calendar = calendar.TextCalendar()
        self.site = self._gen_url(dates)

    def _gen_url(self, dates):
        return SCENARIOS_WEATHER["source_url"]["мэйл"]["weather"]\
            .format(city=check_city(t_crypt), name_month=self._get_name_month(dates))

    @staticmethod
    def find_correct_city_name():
        """поиск города, если модуль "translit_test" не справился"""
        try:
            res = requests.get(SCENARIOS_WEATHER["source_url"]["мэйл"]["search"] + SCENARIOS_WEATHER['city'])
            if res.status_code == 200:
                city = res.url.split('/')[-2]
                if city != 'search':
                    return city
                else:
                    bs = BeautifulSoup(res.text, features='html.parser')
                    city = [el.contents[1].attrs['href'] for el in
                            bs.find_all('div', {'class': 'city__item'})
                            ][0]
                    return city.split('/')[-2]
        except Exception as e:
            raise FindCityError(e)

    def _get_name_month(self, month):
        lang = 'en-US' if os.name != 'posix' else 'en_US.UTF-8'
        locale.setlocale(locale.LC_ALL, lang)
        if month.year == 2020:
            add_year = ''
        else:
            add_year = f'/#{month.year}'
        return '{}-{}{}/#{}'.format(month.day,
                                    self.date_in_calendar.formatmonthname(theyear=2020, themonth=month.month, width=1,
                                                                          withyear=False).lower(),
                                    add_year, 2020)

    def temp_weather(self, bs):
        """аккумуляция температур"""
        LOG.info(f"Смотрим погоду через Mail.ru в - {SCENARIOS_WEATHER['city']}")
        temp_list = [el.text for el in
                     bs.find_all('div', {'class': 'day__temperature'})[0:4]
                     ]
        return temp_list[1:] + temp_list[:1]

    def weather(self, bs):
        """аккумуляция погод"""
        weather_list = [el.contents[1].text for el in
                        bs.find_all('div', {'class': 'day__description'})][0:4]
        return weather_list[1:] + weather_list[:1]

    def __repr__(self):
        return self.site
