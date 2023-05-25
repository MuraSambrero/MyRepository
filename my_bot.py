import telebot
import logging
import requests
from bs4 import BeautifulSoup
import lxml
from value import TOKEN
import re
import pandas as pd

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
		bot.reply_to(message, f'Ищем информацию по данному авто. \
			Просьба подождать.')

	# Сразу создаю словарь в котором будут храниться атрибуты которые мы найдем
		all_attributes = {'Year':[], 'Volume':[], 'Price':[],\
						  'Transmissions':[], 'Drive_type':[],\
						  'Car_type':[], 'Color':[], 'Mileage':[],\
						  'Wheel':[], 'Generation':[],'Complectation':[]}

	# Создаю запрос на сайт, и достаю ссылки со страницы
		if len(name_car) == 2:
			request_site = requests.get(f'https://auto.drom.ru/{name_car[0]}/{name_car[1]}/')
		elif len(name_car) == 3:
			request_site = requests.get(f'https://auto.drom.ru/{name_car[0]}/{name_car[1]}_{name_car[2]}/')
		elif len(name_car) == 4:
			request_site = requests.get(f'https://auto.drom.ru/{name_car[0]}/{name_car[1]}_{name_car[2]}_{name_car[3]}/')

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
			request_site1 = requests.get(all_web_ssilki[i])
			soup_for_attr = BeautifulSoup(request_site1.text, 'lxml')

	# Определяю каждый из атрибутов
			year = soup_for_attr.find('h1', class_ = 'css-1tjirrw e18vbajn0').get_text()
			year = re.findall('\d+', str(year)) # Год
			volume = soup_for_attr.find('span', class_ = 'css-1jygg09 e162wx9x0').get_text() # Объем двиг.
			price = soup_for_attr.find('div', class_ = 'css-eazmxc e162wx9x0').get_text()
			price = price.replace('\xa0', ' ') # Цена
			others_attr = soup_for_attr.findAll('td', class_ = 'css-9xodgi ezjvm5n0') # Определяю более подходящий класс для поиска остальных переменных
			transmission = others_attr[2].string # Трансмиссия
			drive_type = others_attr[3].string # Привод
			car_type = others_attr[4].string # Тип авто(седан, купе и т.д.)
			color = others_attr[5].string # Цвет

			"""По некторым моделям, поиск атрибутов отличается(Индекс приходится смещать)"""
			if color == None:
				color = others_attr[4].string
				car_type = None
			if car_type == None:
				mileage = others_attr[5].get_text()
				mileage = mileage.replace('\xa0', ' ')
				wheel = others_attr[6].get_text()
			else:
				mileage = others_attr[6].get_text()
				mileage = mileage.replace('\xa0', ' ')
				wheel = others_attr[7].string

			"""Здесь мы выборочно используем исключения. 
			Т.к. чаще всего именно этих данных нет на странице.
			А по факту процесс определения атрибутов продолжается"""
			try:
				generation = others_attr[8].get_text()
			except IndexError:
				generation = None
			try:
				complectation = others_attr[9].string
			except IndexError:
				complectation = None

	# Создаем список с атрибутами, чтобы в будущем можно было добавить каждый атрибут в словарь.
			attribute = [year, volume, price, transmission, drive_type, car_type, color,\
						mileage, wheel, generation, complectation]

	# Добавим все атрибуты в словарь
			for i, v in zip(all_attributes.keys(), attribute):
				all_attributes[i].append(v)

	# Создадим дата фрейм(таблицу) с нашими атрибутами
		df = pd.DataFrame(all_attributes)

	# Сохраняем дата фрейм на сервер(ПК)
		df.to_excel(r'C:\\Users\\Admin\\Desktop\\Курс Python - разработчик\\My project\\bot\\Сars.xlsx')

	# Бот отправляет нам созданный файл
		bot.send_document(message.chat.id, open('C:\\Users\\Admin\\Desktop\\Курс Python - разработчик\\My project\\bot\\Сars.xlsx', 'rb'))

	# Данный блок также отправляет сообщению пользователю если не верно было введено название
	else:
		bot.reply_to(message, 'Вы ввели неверные символы или\
			ввели только марку или модель.\
			Пожалуйста попробуйте заново. Нажмите "/start"')


if __name__ == '__main__':
	bot.polling(none_stop=False)