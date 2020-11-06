import functools
import re

from collections import defaultdict, namedtuple

from weather_source.source_api import BaseWeather
from weather_source.functions_subworkers import analyze_weather


def parse_func(func):
    total_weathers_stat = defaultdict(dict)
    Record = namedtuple('Record', 'date temp weather')
    list_data = []

    @functools.wraps(func)
    def surrogate(weather_maker_obj, total_weather_info):
        if weather_maker_obj.stat_mode:
            for day in total_weather_info:
                if day.date not in total_weathers_stat:
                    total_weathers_stat[day.date] = {
                        'temp': [int(re.sub("°", '', temp)) for temp in day.temp],
                        'weather': list(day.weather)
                    }
                else:
                    formatting_temp = [int(re.sub("°", '', temp)) for temp in day.temp]
                    total_weathers_stat[day.date]['temp'] = \
                        [
                            sum(value_temp) // 2 for value_temp in zip(formatting_temp,
                                                                       total_weathers_stat[day.date]['temp'])
                        ]
                    total_weathers_stat[day.date]['weather'] = \
                        [
                            analyze_weather(list(i)) for i in zip(day.weather,
                                                                  total_weathers_stat[day.date]['weather'])
                        ]
            if weather_maker_obj.service_source == 'WeatherMap':
                for day, weather in total_weathers_stat.items():
                    list_data.append(Record(date=day,
                                            temp=[BaseWeather.string_mod(str_temp)
                                                  for str_temp in weather['temp']],
                                            weather=weather['weather']))
                return func(weather_maker_obj, list_data)
        else:
            return func(weather_maker_obj, total_weather_info)

    return surrogate
