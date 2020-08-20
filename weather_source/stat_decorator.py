import functools
import re

from collections import defaultdict, namedtuple

from weather_source.source_api import BaseWeather
from weather_source._functions_subworkers import analyze_weather


def parse_func(func):
    total_weathers_stat = defaultdict(dict)
    Record = namedtuple('Record', 'date temp weather')
    list_data = []

    @functools.wraps(func)
    def surrogate(*args, **kwargs):
        if args[0].stat_mode:
            for i in args[1]:
                if i.date not in total_weathers_stat:
                    total_weathers_stat[i.date] = {'temp': [int(re.sub("°", '', i)) for i in i.temp],
                                                   'weather': list(i.weather)}  # weather из setting
                else:
                    formatting_temp = [int(re.sub("°", '', i)) for i in i.temp]
                    total_weathers_stat[i.date]['temp'] = \
                        [sum(i) // 2 for i in zip(formatting_temp, total_weathers_stat[i.date]['temp'])]
                    total_weathers_stat[i.date]['weather'] = \
                        [analyze_weather(list(i)) for i in zip(i.weather, total_weathers_stat[i.date]['weather'])]
            if args[0].source_weather == 'api':
                for i, j in total_weathers_stat.items():
                    list_data.append(Record(date=i, temp=[BaseWeather.string_mod(str_temp) for str_temp in j['temp']],
                                            weather=j['weather']))
                return func(args[0], list_data)
        else:
            return func(args[0], args[1])

    return surrogate

