import datetime
import io
import unittest
from unittest.mock import patch
import cv2
from termcolor import cprint
from weather_source.translit_city import t_crypt, t_late
import weather_source.user_represent


def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code, text=None):
            self.json_data = json_data
            self.status_code = status_code
            self.text = text

        def json(self):
            return self.json_data

    if args[0] == 'http://api.openweathermap.org/data/2.5/find':
        return MockResponse(json_data={'list': [{'name': GlobalEngineTest.TEST_DICT_TLATE[kwargs['params']['q']]}]},
                            status_code=200, text='тестируем')

    return MockResponse(None, 404)


class GlobalEngineTest(unittest.TestCase):
    TEST_DICT_TLATE = {'москва': 'moscow', 'санкт-петербург': 'saint-petersburg', 'улан-удэ': 'ulan-ude',
                       'йошкар-ола': 'yoshkar-ola', 'рязань': 'ryazan'}
    CORRECT_TLATE = ['moskva', 'sankt-peterburg', 'ulan-ude', 'yoshkar-ola', 'ryazan']

    def setUp(self):
        cprint(f'Вызван {self.shortDescription()}', flush=True, color='cyan')

    def tearDown(self):
        cprint(f'Оттестировано. \n', flush=True, color='grey')

    @patch('weather_source.translit_city.requests.get', side_effect=mocked_requests_get)
    def test_translit(self, mock_get):
        """Тест транслитерации названий городов"""
        for idx, city in enumerate(list(self.TEST_DICT_TLATE.keys())):
            self.assertEqual(self.CORRECT_TLATE[idx], t_crypt(city))
        for idx, city in enumerate(list(self.TEST_DICT_TLATE.keys())):
            self.assertEqual(self.TEST_DICT_TLATE[city], t_late(city))


if __name__ == '__main__':
    unittest.main()
