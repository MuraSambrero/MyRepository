import requests
from bs4 import BeautifulSoup
import re
from my_bot import *

def find_attr(refs_on_the_page,x):
    request_site1 = requests.get(refs_on_the_page[x])
    soup_for_attr = BeautifulSoup(request_site1.text, 'lxml')

      # Определяю каждый из атрибутов
    city_and_year = soup_for_attr.find('h1', class_ = 'css-1tjirrw e18vbajn0').get_text()
    city = f'В {(city_and_year.split())[-1]}'
    if len(city_and_year) < 1:
        year = (re.findall('\d+', str(city_and_year)))[0]
    else:
        try:
            year = (re.findall('\d+', str(city_and_year)))[1]
        except IndexError:
            year = (re.findall('\d+', str(city_and_year)))[0]
    volume = soup_for_attr.find('span', class_ = 'css-1jygg09 e162wx9x0').get_text() # Объем двиг.
    price = soup_for_attr.find('div', class_ = 'css-eazmxc e162wx9x0').get_text()
    price = price.replace('\xa0', ' ') # Цена
    others_attr = soup_for_attr.findAll('td', class_ = 'css-9xodgi ezjvm5n0') # Определяю более подходящий класс для поиска остальных переменных
    transmission = others_attr[2].string # Трансмиссия
    drive_type = others_attr[3].string # Привод
    car_type = others_attr[4].string # Тип авто(седан, купе и т.д.)
    if car_type == None:
        color = others_attr[4].string
        mileage = others_attr[5].get_text()
        mileage = mileage.replace('\xa0', ' ')
        try:
            wheel = others_attr[6].get_text()
        except IndexError:
            wheel = None
        try:
            generation = others_attr[7].string
        except IndexError:
            generation = None
        try:
            complectation = others_attr[9].string
        except IndexError:
            complectation = None
    else:
        color = others_attr[5].string # Цвет
        mileage = others_attr[6].get_text()
        mileage = mileage.replace('\xa0', ' ')
        try:
            wheel = others_attr[7].string
        except IndexError:
            wheel = None
        try:
            generation = others_attr[8].get_text()
        except IndexError:
            generation = None
        try:
            complectation = others_attr[9].string
        except IndexError:
            complectation = None

    attribute = [city, year, volume, price, transmission, drive_type, car_type, color, \
                 mileage, wheel, generation, complectation]
    return attribute