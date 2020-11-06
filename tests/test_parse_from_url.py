import datetime
import logging
import unittest
from unittest.mock import patch
from termcolor import cprint

from weather_source.weather_maker import WeatherMaker


class NewDate(datetime.date):
    @classmethod
    def today(cls):
        return datetime.date(2020, 8, 6)


def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code, text=None):
            self.json_data = json_data
            self.status_code = status_code
            self.text = text

        def json(self):
            return self.json_data

    if args[0] == 'https://pogoda.mail.ru/prognoz/moskva/6-august/#2020':
        return MockResponse(json_data=None, status_code=200, text='тестируем')
    elif args[0] == 'https://yandex.ru/pogoda/moscow/details?via=ms/':
        return MockResponse(json_data=None, status_code=200, text='тестируем')

    return MockResponse(None, 404)


class GlobalEngineTest(unittest.TestCase):
    TEST_FOR_ANALYZE_WEATHER = [(datetime.datetime(2020, 7, 30, 6, 0), '+20', 'ясно'),
                                (datetime.datetime(2020, 7, 30, 9, 0), '+10', 'ясно'),
                                (datetime.datetime(2020, 7, 30, 12, 0), '+18', 'ясно'),
                                (datetime.datetime(2020, 7, 30, 15, 0), '+15', 'ясно'),
                                (datetime.datetime(2020, 7, 30, 18, 0), '+20', 'ясно'),
                                (datetime.datetime(2020, 7, 30, 21, 0), '+17', 'ясно'),
                                (datetime.datetime(2020, 7, 30, 00, 0), '+25', 'ясно'),
                                (datetime.datetime(2020, 7, 30, 3, 0), '+16', 'ясно')]

    def setUp(self):
        logging.disable()
        cprint(f'Вызван {self.shortDescription()}', flush=True, color='cyan')

    def tearDown(self):
        cprint(f'Оттестировано. \n', flush=True, color='grey')

    @patch('weather_source.source_url.YandexWeather.dates_weather', return_value=[datetime.date(2020, 8, 6)])
    @patch('weather_source.source_url.YandexWeather.weather', return_value=['дождь', 'ясно', 'пасмурно', 'гроза'])
    @patch('weather_source.source_url.YandexWeather.temp_weather', return_value=['+19', '+27', '+21', '+15'])
    @patch('weather_source.source_api.requests.get', side_effect=mocked_requests_get)
    @patch('weather_source.weather_maker.BeautifulSoup', return_value=None)
    @patch('logging.FileHandler')
    def test_run_yandex(self, mock_yadates, mock_yaweather, mock_yatemp, mock_get, mock_bs, mocked_log):
        """Тест получения погоды с Яндекс.Погоды"""
        test_ya = WeatherMaker(source=1, city='Москва', dates=['2020.08.06'],
                               command='push')
        test_ya.base_run(name_db='TEST')
        self.assertEqual(len(test_ya.data_weather), 1)

    @patch('weather_source.source_url.MailWeather.weather', return_value=['дождь', 'ясно', 'пасмурно', 'гроза'])
    @patch('weather_source.source_url.MailWeather.temp_weather', return_value=['+19', '+27', '+21', '+15'])
    @patch('weather_source.source_api.requests.get', side_effect=mocked_requests_get)
    @patch('weather_source.weather_maker.BeautifulSoup', return_value=None)
    @patch('logging.FileHandler')
    @patch('locale.setlocale', return_value=None)
    def test_run_mail(self, mock_mailweather, mock_mailtemp, mock_get, mock_bs, mocked_log, mock_locale):
        """Тест получения погоды с mail.ru"""
        test_mail = WeatherMaker(source=2, city='Москва', dates=['2020.08.06'], command='push')
        test_mail.base_run(name_db='TEST')
        self.assertEqual(len(test_mail.data_weather), 1)


if __name__ == '__main__':
    unittest.main()
