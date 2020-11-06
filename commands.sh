#!/usr/bin/env bash

# запуск с параметрами по умолчанию
python give_weather.py push

# запуск с уточнёнными параметрами
python give_weather.py push -s 3 -c Екатеринбург -d 2020.08.12-2020.08.14
python give_weather.py push -s 2 -c Рязань -d 2020.08.12

# запуск с уточнёнными параметрами и "статистическим" режимом
python give_weather.py push -c Екатеринбург -d 2020.08.12-2020.08.14 -st
python give_weather.py push -c Рязань -d 2020.08.12 -st

# печать открытки
python give_weather.py card -c Рязань -d 2020.08.12
python give_weather.py card -c Екатеринбург -d 2020.08.12

# вывод на консоль
python give_weather.py console -c Рязань -d 2020.08.12
python give_weather.py console -c Екатеринбург -d 2020.08.12-2020.08.14