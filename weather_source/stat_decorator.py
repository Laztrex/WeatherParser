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

# TODO: ВОПРОС ПРЕПОДАВАТЕЛЮ. Часть третья.
# TODO: На данном этапе прикрутил такую вот кнопку, но она имеет смысл при объявлении декоратора, и никак не получается
#  управлять возвращаемой функцией в зависимости от параметра (stat_mode). Коли True - до декорируем, обрабатываем,
#  а иначе - отдаем ничего не трогая

# TODO: декоратор знает про аргументы, которые передаются в функцию. Можно взять оттуда stat_mode и в зависимости от проверки
# TODO: выполнять тот или иной код в декораторе или нет (если я правильно вас понял).
# TODO: В любом случае попробуйте потренироваться на кроликах (на более простых примерах)
