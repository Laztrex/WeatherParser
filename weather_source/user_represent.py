import calendar
import os

import cv2
import datetime
import locale
import re
import textwrap

import numpy as np
from random import choice

from weather_source.translit_city import t_crypt
import weather_source.parse_info
from weather_source.files.settings import SCENARIOS_WEATHER
from weather_source.functions_subworkers import return_weather_colored_and_logo

class ImageMaker:
    """
    draw card weather
    """

    def __init__(self, city):
        self.image_cv2 = cv2.imread(SCENARIOS_WEATHER["PATH_TEMP"])
        self.city = city
        self.logo = None

    def _decode_symbol(self, symbol):
        """status function - T (временная)
        По условию - только cv2. Без PIL манипуляцию с шрифтами пока не решил
        Вместо '−' отображаются ???"""
        symbol = symbol.strip('\u00B0')
        if not symbol[0].isdigit():
            if ord(symbol[0]) == 8722 or symbol == '-':
                return '-' + symbol[1]
        return symbol

    def run(self, date, part_day, weather):
        """
        запуск рисования открытки
        :param date: дата
        :param part_day: часть суток
        :param weather: погода (dict)
        """
        self.gen_img(part_day, weather)
        if part_day == 'Ночь':
            self.add_info_text(date)
            self.print_card(date)
            self.init_new()

    def init_new(self):
        self.image_cv2 = cv2.imread(SCENARIOS_WEATHER["PATH_TEMP"])

    def gen_img(self, part_day, weather):
        """генерация изображения, синтез иконок"""
        self.split_jpg(self.add_weather(weather, part_day), part_day)
        self.merge_img_with_icons(img1=self.image_cv2,
                                  icon=SCENARIOS_WEATHER["part_day_icon"][part_day],
                                  mode='part_day',
                                  part_day=part_day)

    def add_info_text(self, date):
        """добавление текста на открытку"""
        self.add_text_date(date)
        self.add_city()
        self.fill_in_text(date)

    def add_city(self):
        """добавление города"""
        city = textwrap.wrap(self.city, width=20)
        coord, font, scale, clr, thickness, line = SCENARIOS_WEATHER["TEXT_CITY"]
        for num, word in enumerate(city):
            cv2.putText(self.image_cv2, str(word), (coord[0], coord[1] + 10 * num), font, scale, clr, thickness, line)
        image_flag = np.asarray(bytearray(weather_source.parse_info.parse_flag_city(self.city).read()), dtype="uint8")
        self.image_cv2[10:45, 430:500] = cv2.resize(cv2.imdecode(image_flag, cv2.IMREAD_COLOR), (70, 35))

    def add_info(self, date, mode, mode_coord):
        """
        инфомационное заполнение (Хроника - события в истории в этот день, В мире - новость в день создания открытки)
        :param date: дата
        :param mode: Хроника/В мире
        :param mode_coord: координаты текста
        """
        x1, y1, x2, y2 = SCENARIOS_WEATHER["TEXT_XY"][mode]
        cv2.line(self.image_cv2, (x1[0], y1[0]), (x1[1], y1[1]), (0, 0, 0), 1)
        cv2.putText(self.image_cv2, str(mode), mode_coord,
                    cv2.FONT_HERSHEY_COMPLEX, 0.3,
                    (0, 0, 5), 1, cv2.LINE_4)
        cv2.line(self.image_cv2, (x2[0], y2[0]), (x2[1], y2[1]), (0, 0, 0), 1)
        event = choice(weather_source.parse_info.parse_chronicle_in_date(date)) if mode == 'Хроника' \
            else choice(weather_source.parse_info.parse_current_news())
        if mode == 'Хроника':
            for num, word in enumerate(event):
                if num == 1:
                    new = textwrap.wrap(event[1], width=24)
                    self.text_parse(new, mode)
                    continue
                cv2.putText(self.image_cv2, str(word), (390 - 45 * num, 168 + 40 * num),
                            cv2.FONT_HERSHEY_COMPLEX, 0.3,
                            (0, 0, 5), 1, cv2.LINE_8)
        else:
            self.text_parse(textwrap.wrap(event, width=24), mode)
            cv2.putText(self.image_cv2, str('yandex.ru'), (440, 138), cv2.FONT_HERSHEY_COMPLEX, 0.3, (0, 0, 5), 1,
                        cv2.LINE_8)
            cv2.putText(self.image_cv2, str(datetime.date.today()), (300, 138), cv2.FONT_HERSHEY_COMPLEX, 0.3,
                        (0, 0, 5), 1, cv2.LINE_8)

    def text_parse(self, text, mode):
        """
        Парсер текста для нанесения на открытку
        :param text: текст события
        :param mode: координата текста
        """
        coord, font, scale, clr, thickness, line = SCENARIOS_WEATHER["TEXT_INFO"]
        for idx, word in enumerate(text):
            if idx == 4:
                cv2.putText(self.image_cv2, '...', (coord[0], coord[1][mode] + 14 * idx),
                            font, scale, clr, thickness, line)
                break
            word_cleared = re.sub(r'[«‎»]', '"', word)
            word_cleared = re.sub(r'[—–]', '-', word_cleared)
            word_cleared = re.sub(r'ё', 'е', word_cleared)
            cv2.putText(self.image_cv2, str(word_cleared), (coord[0], coord[1][mode] + 14 * idx),
                        font, scale, clr, thickness, line)

    def fill_in_text(self, date):
        """Заполнение информационных данных"""
        self.add_info(date, mode='Хроника', mode_coord=(380, 152))
        self.add_info(date, mode='В мире', mode_coord=(380, 62))

    def add_text_date(self, date):
        """Печать даты"""
        coord, font, scale, clr, thickness, line = SCENARIOS_WEATHER["TEXT_DATE"]
        cv2.putText(self.image_cv2, str(date), (coord[0], coord[1]), font, scale, clr, thickness, line)
        locale.setlocale(locale.LC_ALL, '')
        cv2.putText(self.image_cv2, str(calendar.day_name[date.weekday()].lower()), (coord[0], coord[1] + 10), font,
                    scale - 0.1, clr, thickness, line)

    def add_weather(self, weather, part_day):
        """Печать погоды и слияние ColorMap'нутых слоев в зависимсоти от погоды"""
        rectangle_bgr, logo = self.color_back_weather(weather['weather'])  # возврат цветной текстуры для погоды
        returned = self.merge_img_with_icons(img1=rectangle_bgr, icon=logo, mode='weather', part_day=part_day)

        # печать текста погоды
        coord, font, scale, clr, thickness, line = SCENARIOS_WEATHER["TEXT_WEATHER"]
        text = textwrap.wrap(weather['weather'], width=10)

        for i, weather_text in enumerate(text):
            cv2.putText(returned, weather_text, (coord[0], coord[1] + 11 * i), font, scale, clr, thickness, line,
                        bottomLeftOrigin=False)

        # печать температуры
        coord, font, scale, clr, thickness, line = SCENARIOS_WEATHER["TEXT_TEMP"]
        cv2.putText(returned, self._decode_symbol(weather['temp']), coord, font, scale, clr, thickness, line)

        returned = self.merge_img_with_icons(img1=returned, icon=SCENARIOS_WEATHER["degree_icon"], mode='degree',
                                             part_day=part_day)
        return returned

    def split_jpg(self, img2, part_day):
        """Добавляем на макет текстуру для погоды и поля для текста"""
        h, w = SCENARIOS_WEATHER["ICON_WEATHER"][part_day]
        self.image_cv2[h[0]:h[1], w[0]:w[1]] = img2
        img = np.array([250, 230, 230])
        self.image_cv2[h[0]:h[1] + 3, 292:505] = img

    def merge_img_with_icons(self, img1, icon, mode, part_day):
        """
        слияние картинки и иконок
        :param img1: картинка
        :param icon: имя иконки
        :param mode: weather/part_day/degree - меняентся пространство наслоения
        :param part_day: подсмотр координат в зависимости от части суток
        :return: изображение с иконками
        """
        img2 = cv2.imread(SCENARIOS_WEATHER["PATH_ICON"].format(mode=mode, icon=icon))
        brows, bcols = img1.shape[:2]
        rows, cols, channels = img2.shape
        if mode == 'weather':
            roi = img1[0:rows, bcols - rows:bcols]
        elif mode == 'part_day':
            h, w = SCENARIOS_WEATHER["ICON_PART_DAYS"][part_day]
            roi = img1[h[0]:h[1], w[0]:w[1]]
        else:
            x1, x2, y1, y2 = SCENARIOS_WEATHER["ICON_DEGREE"].values()
            roi = img1[y2:y1, x2:x1]
        img2gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        ret, mask = cv2.threshold(img2gray, 10, 255, cv2.THRESH_BINARY)
        mask_inv = cv2.bitwise_not(mask)

        img1_bg = cv2.bitwise_and(roi, roi, mask=mask)
        img2_fg = cv2.bitwise_and(img2, img2, mask=mask_inv)

        dst = cv2.add(img1_bg, img2_fg)
        img2 = dst

        if mode == 'weather':
            img1[0:rows, bcols - rows:bcols] = img2
        elif mode == 'part_day':
            h, w = SCENARIOS_WEATHER["ICON_PART_DAYS"][part_day]
            img1[h[0]:h[1], w[0]:w[1]] = img2
        elif mode == 'degree':
            x1, x2, y1, y2 = SCENARIOS_WEATHER["ICON_DEGREE"].values()
            img1[y2:y1, x2:x1] = img2
        else:
            img1[0:rows, 0:cols] = img2
        return img1

    def color_back_weather(self, weather, opt=(60, 280)):
        """Градиенты и создание цветного слоя в зависимости от погоды"""
        lower_b = np.array([110, 50, 50])
        upper_b = np.array([130, 255, 255])

        s_gradient = np.ones((opt[0], 1), dtype=np.uint8) * np.linspace(lower_b[1], upper_b[1], opt[1], dtype=np.uint8)
        v_gradient = np.rot90(
            np.ones((opt[1], 1), dtype=np.uint8) * np.linspace(lower_b[1], upper_b[1], opt[0], dtype=np.uint8))
        h_array = np.arange(lower_b[0], upper_b[0] + 1)

        h = h_array[0] * np.ones((opt[0], opt[1]), dtype=np.uint8)
        hsv_color = cv2.merge((h, s_gradient, v_gradient))
        color_, logo = self.analyze_weather_color(weather.lower())
        rgb_color = cv2.applyColorMap(hsv_color, color_)
        rgb_color = cv2.rectangle(rgb_color, (0, opt[0] - 2), (opt[1] - 2, 1), (0, 0, 0), 2)
        return rgb_color, logo

    def analyze_weather_color(self, weather):
        """ссылка на цветовую схему погоды в settings.py"""
        return return_weather_colored_and_logo(weather)

    def viewImage(self, image, name_of_window):
        cv2.namedWindow(name_of_window, cv2.WINDOW_NORMAL)
        cv2.imshow(name_of_window, image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def get_io_img(self, name_io_img='test.png'):
        res, im_png = cv2.imencode('.png', self.image_cv2)
        with open(name_io_img, 'wb') as f:
            f.write(im_png.tobytes())
        success, buffer = cv2.imencode(".jpg", self.image_cv2, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        buffer.tofile('ExtensionlessFile')

    def print_card(self, date):
        """Печать открытки"""
        path = os.path.join(SCENARIOS_WEATHER["media_root"].format(city=t_crypt(self.city.lower()),
                                                                   year=date.year,
                                                                   month=date.month))
        os.makedirs(path, exist_ok=True)
        cv2.imwrite(os.path.join(path, f'{date.day}.jpg'), self.image_cv2)
