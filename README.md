# WeatherParser
share the weather, upload to the database, draw a postcard, and display information on the console
> Globally: it is planned to supplement the project, add new resources and make English support
>> Warining! Cities temporarily only in Cyrillic
---
## Description
Weather parser from three sources - yandex.ru, mail.ru and API WeatherOpenMap  
Capability:  
- **getting the weather from yandex.ru (яндекс) and add in database** 
~~~
# default city: Москва
# default resource: яндекс
# default dates: one week future
python3 give_weather.py push

# equivalently
python3 give_weather.py push -s яндекс
~~~
~~~
# with choice city
python3 give_weather.py push -c Рязань
~~~
> WARNING! Source "яндекс" supports only 10 days  
- **getting the weather from mail.ru and add in database** 
~~~
python3 give_weather.py push -s мэйл
~~~
~~~
# with choices dates and city
python3 give_weather.py push -s мэйл -c Рязань -d 2020.08.12
~~~

- **getting the weather from WeatherOpenMap and add in database** 
~~~
python3 give_weather.py push -s api -c Екатеринбург
~~~
~~~
python3 give_weather.py push -s api -c Рязань -d 2020.08.12-2020.08.15
~~~
> WARNING!  
>Add your id key WeatherOpenMap in _/weather_source/file/settings.py_ 
>> WARNING!  
>Source "api" supports only 5 days

- **getting the weather from all resources (stat_mode) and add in database** 
~~~
python3 give_weather.py push -st -c Екатеринбург
~~~
~~~
python3 give_weather.py push -st -c Рязань -d 2020.08.12-2020.08.15
~~~

- **draw postcard (_use cv2_)** 
~~~
python3 give_weather.py card -c Рязань -d 2020.08.17
~~~
~~~
python3 give_weather.py card -c Москва -d 2020.08.12-2020.08.15
~~~
> Example postcard
~~~
python3 give_weather.py card -c Рязань -d 2020.08.17
~~~
![Image alt](https://github.com/Laztrex/WeatherParser/raw/master/tests/test_img.jpg)