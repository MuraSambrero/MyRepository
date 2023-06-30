import time

import telebot
import logging
import requests
from bs4 import BeautifulSoup
import lxml
from value import TOKEN
import re
import pandas as pd
from func_attr import *
from time import sleep

count = 0
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG) # Включаем логгирование

bot = telebot.TeleBot(TOKEN) # Сам токен храним в другом файле. Здесь просходит идентификация(код - бот)

@bot.message_handler(commands=['start']) # Бот принимает сообщение от пользователя
def send_welcome(message):
	bot.reply_to(message, 'Привет! Какую машину вы ищете?\
	\nПросьба писать запрос как в примере:\
	\n"toyota allion"')

@bot.message_handler(content_types=['text'])
def enter_car(message):
	name_car = message.text.lower() # Добавляем данные введеные пользователем в переменную

	# Здесь мы проверяем корректно ли введено название
	if ' ' in name_car:
		for i in name_car:
			if (ord(i) in list(range(97,123))) or (ord(i) \
				in list(range(49,58))) or (ord(i) \
				in list(range(1072,1103))) or (ord(i) == 32):
				continue
			else:
				bot.reply_to(message, 'Вы ввели неверные символы.\
				 Пожалуйста попробуйте заново. Введите "/start"')
				break

        # Делим на отдельные срезы название авто которое ввел пользователь
		name_car = name_car.split()
		bot.reply_to(message, f'Ищем информацию по данному авто.\
			Просьба подождать.')

	    # Сразу создаю словарь в котором будут храниться атрибуты которые мы найдем
		all_attributes = {'City':[], 'Year':[], 'Volume':[], 'Price':[],\
						  'Transmissions':[], 'Drive_type':[],\
						  'Car_type':[], 'Color':[], 'Mileage':[],\
						  'Wheel':[], 'Generation':[],'Complectation':[]}

		all_web_ssilki = [1]
		num_page = 1
		while len(all_web_ssilki) != 0:
			try:
				all_web_ssilki = []
				page = f'page{num_page}'
				if num_page == 1:
					if len(name_car) == 2:
						request_site = requests.get(f'https://auto.drom.ru/{name_car[0]}/{name_car[1]}/')
					elif len(name_car) == 3:
						if name_car[0].lower() == 'alfa' and name_car[1].lower() == 'romeo':
							request_site = requests.get(f'https://auto.drom.ru/{name_car[0]}_{name_car[1]}/{name_car[2]}/')
						else:
							request_site = requests.get(f'https://auto.drom.ru/{name_car[0]}/{name_car[1]}_{name_car[2]}/')
					elif len(name_car) == 4:
						request_site = requests.get(f'https://auto.drom.ru/{name_car[0]}/{name_car[1]}_{name_car[2]}_{name_car[3]}/')
					soup = BeautifulSoup(request_site.text, 'lxml')
					all_ssilki = soup.findAll('a', class_='css-xb5nz8 e1huvdhj1')
				elif num_page > 1:
					if len(name_car) == 2:
						request_site = requests.get(f'https://auto.drom.ru/{name_car[0]}/{name_car[1]}/{page}/')
					elif len(name_car) == 3:
						if name_car[0].lower() == 'alfa' and name_car[1].lower() == 'romeo':
							request_site = requests.get(f'https://auto.drom.ru/{name_car[0]}_{name_car[1]}/{name_car[2]}/{page}/')
						else:
							request_site = requests.get(f'https://auto.drom.ru/{name_car[0]}/{name_car[1]}_{name_car[2]}/{page}/')
					elif len(name_car) == 4:
						request_site = requests.get(f'https://auto.drom.ru/{name_car[0]}/{name_car[1]}_{name_car[2]}_{name_car[3]}/{page}/')
					soup = BeautifulSoup(request_site.text, 'lxml')
					all_ssilki = soup.findAll('a', class_='css-xb5nz8 e1huvdhj1')

				# Сохраняю запрошенную страницу для себя на просмотр возможных ошибок
				with open("C:\\Users\\Admin\\Desktop\\Курс Python - разработчик\\My project\\bot\\response.txt", "w") as f:
					f.write(request_site.text)

				# С помощью библиотеки bs4 сохраняю необходимую часть html в переменную all_ssilki
				soup = BeautifulSoup(request_site.text, 'lxml')
				all_ssilki = soup.findAll('a', class_ = 'css-xb5nz8 e1huvdhj1')

				# Здесь мы создаем список из ссылок(на авто запрошенной модели) которые есть на странице
				all_web_ssilki = [all_ssilki[i]['href'] for i in range(len(all_ssilki))]

				# С этого момента заходим на каждую ссылку с авто на странице
				for i in range(len(all_web_ssilki)):
					attribute = find_attr(all_web_ssilki, i)

					# Добавим все атрибуты в словарь
					for i, v in zip(all_attributes.keys(), attribute):
						all_attributes[i].append(v)

				num_page += 1
			except:
				time.sleep(3)

	    # Создадим дата фрейм(таблицу) с нашими атрибутами
		df = pd.DataFrame(all_attributes)

	    # Сохраняем дата фрейм на сервер(ПК)
		df.to_excel(f'C:\\Users\\Admin\\Desktop\\Курс Python - разработчик\\My project\\bot\\{name_car[0]}.xlsx')

	    # Бот отправляет нам созданный файл
		bot.send_document(message.chat.id, open(f'C:\\Users\\Admin\\Desktop\\Курс Python - разработчик\\My project\\bot\\{name_car[0]}.xlsx', 'rb'))

	# Данный блок также отправляет сообщению пользователю если не верно было введено название
	else:
		bot.reply_to(message, 'Вы ввели неверные символы или\
			ввели только марку или модель.\
			Пожалуйста попробуйте заново. Нажмите "/start"')


if __name__ == '__main__':
	bot.polling(none_stop=False)