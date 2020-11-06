import logging

import cv2
import datetime
import io
import unittest

from datetime import date
from termcolor import cprint
from unittest.mock import patch
from weather_source.user_represent import ImageMaker


class NewDate(date):
    @classmethod
    def today(cls):
        return date(2020, 8, 17)


class GlobalEngineTest(unittest.TestCase):
    TEST_IMG_ARRAY = None

    def setUp(self):
        self.get_weather_test = \
            ImageMaker(city='Ставрополь')
        cprint(f'Вызван {self.shortDescription()}', flush=True, color='cyan')

    def tearDown(self):
        cprint(f'Оттестировано. \n', flush=True, color='grey')

    @patch('cv2.imwrite')
    @patch('os.makedirs')
    @patch('weather_source.parse_info.parse_current_news',
           return_value=['В Белоруссии оппозиция опубликовала состав координационного совета'])
    @patch('weather_source.parse_info.parse_chronicle_in_date',
           return_value=[('1896', 'Начало золотой лихорадки на Клондайке', 'https://www.calend.ru/events/3036/')])
    @patch('weather_source.user_represent.ImageMaker.init_new', return_value=None)
    def test_generate_card(self, mock_img, mock_dir, mock_news, mock_chronicle, mock_init):
        datetime.date = NewDate

        flag_city = open('test_flag', 'rb')
        with patch('weather_source.parse_info.parse_flag_city', return_value=flag_city):
            for i, j in [('Утро', {'temp': '+18', 'weather': 'ясно'}),
                         ('День', {'temp': '+25', 'weather': 'ясно'}),
                         ('Вечер', {'temp': '+19', 'weather': 'ясно'}),
                         ('Ночь', {'temp': '+12', 'weather': 'облачно'})]:
                self.get_weather_test.run(date=date(2020, 8, 17), part_day=i, weather=j)
        flag_city.close()

        duplicate = self.get_weather_test.image_cv2
        s_success1, buffer = cv2.imencode(".jpg", duplicate)
        duplicate_io = io.BytesIO(buffer)

        with open('test_img.jpg', 'rb') as original:
            self.assertEqual(original.read(), duplicate_io.read())


if __name__ == '__main__':
    unittest.main()
