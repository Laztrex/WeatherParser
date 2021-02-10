#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import datetime
import sys

from weather_source.weather_maker import WeatherMaker


def get_weather(**kwargs):
    maker = WeatherMaker(**kwargs)
    maker.base_run()


def create_parser():
    today_date = datetime.date.today()
    future_week = f'{today_date.strftime("%Y.%m.%d")}-' \
                  f'{(today_date + datetime.timedelta(days=7)).strftime("%Y.%m.%d")}'

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')

    push_parser = subparsers.add_parser('push')
    push_parser.add_argument('-s', '--source',
                             default=1,
                             help='Источник погоды, опционально. По умолчанию - Яндекс.Погода',
                             type=int)
    push_parser.add_argument('-c', '--city',
                             default='Москва',
                             help='Город, опционально')
    push_parser.add_argument('-d', '--dates',
                             default=[future_week],
                             nargs='+',
                             help='Даты, опционально. По умолчанию - неделя')
    push_parser.add_argument('-st', '--stat_mode',
                             action='store_true')

    pull_parser = subparsers.add_parser('pull')
    pull_parser.add_argument('-c', '--city',
                             default='Москва',
                             help='Город, опционально')
    pull_parser.add_argument('-d', '--dates',
                             default=[future_week],
                             nargs='+',
                             help='Даты, опционально. По умолчанию - будущая неделя')

    card_parser = subparsers.add_parser('card')
    card_parser.add_argument('-c', '--city',
                             default='Москва',
                             help='Город, опционально')
    card_parser.add_argument('-d', '--dates',
                             default=[(today_date + datetime.timedelta(days=1)).strftime("%Y.%m.%d")],
                             nargs='+',
                             help='Даты, опционально. ')

    console_parser = subparsers.add_parser('console')
    console_parser.add_argument('-d', '--dates',
                                default=[future_week],
                                nargs='+',
                                help='Даты, опционально. По умолчанию - неделя')
    console_parser.add_argument('-c', '--city',
                                default='Москва',
                                help='Город, опционально')

    return parser


if __name__ == '__main__':
    parser = create_parser()
    namespace = parser.parse_args(sys.argv[1:])
    get_weather(**namespace.__dict__)
