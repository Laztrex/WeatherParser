#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import datetime
import sys

from weather_source.weather_maker import WeatherMaker


def get_weather(source=None, date=None, city=None, push_base=None, pull_base=None, card=None, console=None,
                stat_mode=None):
    maker = WeatherMaker(source=source, city=city, push_base=push_base, pull_base=pull_base,
                         card=card, date=date, console=console, stat=stat_mode)
    maker.base_run()


def create_parser():
    current = datetime.date.today()
    future = f'{current.strftime("%Y.%m.%d")}-' \
             f'{(current + datetime.timedelta(days=7)).strftime("%Y.%m.%d")}'

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')

    push_parser = subparsers.add_parser('push')
    push_parser.add_argument('-s', '--source', default='яндекс',
                             help='Источник погоды, опционально. По умолчанию - Яндекс.Погода')
    push_parser.add_argument('-c', '--city', default='Москва', help='Город, опционально')
    push_parser.add_argument('-d', '--dates', default=[future], nargs='+',
                             help='Даты, опционально. По умолчанию - неделя')
    push_parser.add_argument('-st', '--stat_mode', action='store_true')

    pull_parser = subparsers.add_parser('pull')
    pull_parser.add_argument('-c', '--city', default='Москва', help='Город, опционально')
    pull_parser.add_argument('-d', '--dates', default=[future], nargs='+',
                             help='Даты, опционально. По умолчанию - будущая неделя')

    card_parser = subparsers.add_parser('card')
    card_parser.add_argument('-c', '--city', default='Москва', help='Город, опционально')
    card_parser.add_argument('-d', '--dates', default=current.strftime("%Y.%m.%d"), nargs='+',
                             help='Даты, опционально')

    console_parser = subparsers.add_parser('console')
    console_parser.add_argument('-d', '--dates', default=[future], nargs='+',
                                help='Даты, опционально. По умолчанию - неделя')
    console_parser.add_argument('-c', '--city', default='Москва', help='Город, опционально')

    return parser


if __name__ == '__main__':
    parser = create_parser()
    namespace = parser.parse_args(sys.argv[1:])

    if namespace.command == "push":
        get_weather(source=namespace.source, date=namespace.dates, city=namespace.city, push_base=True,
                    stat_mode=namespace.stat_mode)
    elif namespace.command == "pull":
        get_weather(date=namespace.dates, city=namespace.city, pull_base=True)
    elif namespace.command == "card":
        get_weather(date=namespace.dates, city=namespace.city, card=True)
    elif namespace.command == "console":
        get_weather(date=namespace.dates, city=namespace.city, console=True)
    else:
        print("Что-то пошло не так...")

