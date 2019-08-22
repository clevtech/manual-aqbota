#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Bauyrzhan Ospan"
__copyright__ = "Copyright 2018, Aqbota"
__version__ = "1.0.1"
__maintainer__ = "Bauyrzhan Ospan"
__email__ = "bospan@cleverest.tech"
__status__ = "Development"

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
import requests
import xml.dom.minidom
import datetime
import re
from random import sample
import socket
import json
import os
from pathlib import Path
import glob
import logging


logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)-15s]: %(message)s'
)

datafolder = os.path.abspath(__file__).split("main.py")[0]

TELEGRAM_TOKEN = '942402785:AAHdH7jhutO_dge_4DKa1jWGemXAI5SrZHY'

bot = telebot.TeleBot(TELEGRAM_TOKEN)

adminID = "-1001286114767"
godID = "-323859236"

points = {"Astana Hub": ["51.088513", "71.413808"], \
    "Mega Silkway": ["51.088769" ,"71.411976"], \
        "AIFC": ["51.087676", "71.414830"]}


def back(barcode):
    barcode = barcode.replace("\n", "")
    url = "http://pls-test.post.kz/api/service/postamat?wsdl"

    headers = {'content-type': 'text/xml'}

    file_name = datafolder + "templates/given.xml"

    with open(file_name, "r") as file:
        req = file.read()
        req = req.replace("BARCODE", barcode)

    response = send_post(url, data=req.replace("\n", "").encode('utf-8'), headers=headers)

    status = re.findall("<ns3:code>(.*?)</ns3:code>", str(response.content.decode("utf-8")))[0]

    info = re.findall("<ns3:name>(.*?)</ns3:name>", str(response.content.decode("utf-8")))[0]

    return status, info


def given(barcode):
    barcode = barcode.replace("\n", "")
    url = "http://pls-test.post.kz/api/service/postamat?wsdl"

    headers = {'content-type': 'text/xml'}

    file_name = datafolder + "templates/given.xml"

    with open(file_name, "r") as file:
        req = file.read()
        req = req.replace("BARCODE", barcode)

    response = send_post(url, data=req.replace("\n", "").encode('utf-8'), headers=headers)

    status = re.findall("<ns3:code>(.*?)</ns3:code>", str(response.content.decode("utf-8")))[0]

    info = re.findall("<ns3:name>(.*?)</ns3:name>", str(response.content.decode("utf-8")))[0]

    return status, info


def add_new_user(number, ids):
    if number[0] == "8":
        number = "+7" + number[1::]
    spisok = glob.glob(datafolder + "db/users/*")
    print(spisok)
    newfile = datafolder + "db/users/" + number
    with open(newfile, 'w') as newf:
        newf.write(str(ids))
        logging.info("Added new user: " + number + " with id: " + str(ids))
    return True


def find_user(number):
    if number[0] == "8" or number[0] == "7":
        number = "+7" + number[1::]
    spisok = glob.glob(datafolder + "db/users/*")
    ids = None
    for user in spisok:
        user_num = user.split("/")[-1]
        if user_num == number:
            with open(user, 'r') as out:
                ids = out.readline().strip("\n")
                logging.info("Found user: " + ids)
    if ids == None:
        logging.info("There is no user with phone: " + number)
    return ids


def send_post(url, data, headers):
    while 1:
        try:
            res = requests.post(url, data, headers)
            break
        except:
            logging.warning("Сервер не дает ответа, пробую еще раз")
    return res


def send_main_menu():
    markup = ReplyKeyboardMarkup()
    markup.row_width = 1
    markup.add(KeyboardButton('Проверить посылку'))
    bot.send_message(adminID, "Главное меню", reply_markup=markup)


def gen_markup():
    markup = ReplyKeyboardMarkup()
    markup.row_width = 1
    markup.add(KeyboardButton('Да (Отправить мой номер)', True),
                               KeyboardButton("Нет"))
    return markup


def pus_data(barcode):
    barcode = barcode.replace("\n", "")
    url = "http://pls-test.post.kz/api/service/postamatHierarchy?wsdl"
    url2 = "http://pls-test.post.kz/api/service/postamat?wsdl"

    headers = {'content-type': 'text/xml'}

    file_name = datafolder + "/templates/GETDATA.xml"
    file_name2 = datafolder + "/templates/chech_money.xml"

    with open(file_name, "r") as file:
        req = file.read()
        req = req.replace("BARCODE", barcode)

    response = send_post(url, data=req.replace("\n", "").encode('utf-8'), headers=headers)
    status = re.findall("<ResponseText>(.*?)</ResponseText>", str(response.content.decode("utf-8")))[0]
    
    if status != "Success":
        logging.warning("There is no such payload: " + barcode)
        responce = "Проверил по ШПИ №" + barcode + \
        ". Вышла ошибка: " + status + "."
    
        bot.send_message(adminID, responce)
        send_main_menu()
        return False

    log = {
        'barcode': barcode,
        "client": re.findall("<Rcpn>(.*?)</Rcpn>", str(response.content.decode("utf-8")))[0],
        "time": datetime.datetime.now(),
        "phone": re.findall("<RcpnPhone>(.*?)</RcpnPhone>", str(response.content.decode("utf-8")))[0]
    }
    responce = "Проверил адресата " + log["client"] + " по ШПИ №" + log["barcode"] + \
        " с номером " + log["phone"] + ". Проверяю наложный платеж, пожалуйста, подождите."
    
    bot.send_message(adminID, responce)

    with open(file_name2, "r") as file:
        req = file.read()
        req = req.replace("BARCODE", barcode)

    response2 = send_post(url2, data=req.replace("\n", "").encode('utf-8'), headers=headers)

    cash_check = re.findall("<ns2:amount>(.*?)</ns2:amount>", str(response2.content))
    if cash_check:
        if cash_check[0] != "0":
            cash_check = False
        else:
            cash_check = True
    else:
        cash_check = True

    if cash_check:
        responce = "Наложный платеж отсуствует. Проверяю пользователя в базе данных. Пожалуйста, ждите."
        bot.send_message(adminID, responce)
    else:
        responce = "Наложный платеж присуствует. Не могу доставлять посылки с платежом."
        bot.send_message(adminID, responce)
        send_main_menu()
        return False

    ids = find_user(log["phone"])
    if ids:
        responce = "Этот пользователь зарегистрирован в нашей системе."
        markup = ReplyKeyboardMarkup()
        markup.row_width = 1
        with open(datafolder + "db/box.json", 'w') as database:
            data = {'id': ids, 'name': log["client"], 'spi': barcode, 'address': None, 'start': None}
            json.dump(data, database)
        markup.add(KeyboardButton('Посылка в роботе'),
                                KeyboardButton("Отмена"))
        bot.send_message(adminID, responce, reply_markup=markup)
        bot.send_message(godID, "Open door")
    else:
        responce = "Этот пользователь не пользуется нашим ботов в телеграм. Отмена."
        bot.send_message(adminID, responce)
        send_main_menu()


def income(barcode):
    barcode = barcode.replace("\n", "")
    url = "http://pls-test.post.kz/api/service/postamat?wsdl"

    headers = {'content-type': 'text/xml'}

    file_name = datafolder + "templates/INCOME.xml"

    with open(file_name, "r") as file:
        req = file.read()
        req = req.replace("BARCODE", barcode)
        logging.info("Sending barcode to save payload.")

    response = send_post(url, data=req.replace("\n", "").encode('utf-8'), headers=headers)


    status = re.findall("<ns3:code>(.*?)</ns3:code>", str(response.content.decode("utf-8")))[0]

    info = re.findall("<ns3:name>(.*?)</ns3:name>", str(response.content.decode("utf-8")))[0]

    return status, info

# Handle '/start' and '/help'
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_sticker(message.chat.id, "CAADAgADLAEAAtrHBgABY61OMYcskVEWBA")
    bot.send_message(message.chat.id, """\
    Добрый день!
    Меня зовут робот-курьер 'Aqbota', и я работаю на АО 'Казпочта'.
    Чтобы продолжить работу со мной, Вам необходимо подтвердить Вашу личность.
    Пожалуйста, нажмите 'Да', если Вы согласны, или 'Нет', если не согласны.\
    """, reply_markup=gen_markup())


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def main_messages(message):
    if message.text == "Нет":
        bot.reply_to(message, "Хорошо, если вдруг передумаете, нажмите на кнопку 'Да'", 
        reply_markup=gen_markup())
    
    elif message.text == "Я не приду":
        markup = ReplyKeyboardMarkup()
        markup.row_width = 1
        markup.add(KeyboardButton('GOD: Домой'))
        bot.send_message(godID, "Не придут, отмена, домой.", reply_markup=markup)
        bot.send_message(adminID, "Клиент отменил поездку. Выезжаю обратно в офис.")
        bot.reply_to(message, "Хорошо, тогда я поехала обратно в офис АО 'Казпочта'")

    elif message.text == "Проверить посылку" and str(message.chat.id) == str(adminID):
        bot.send_message(adminID, "Введите ШПИ в формате 'KZ112345678KZ', пожалуйста.")
        
    elif message.text == "Отмена" and str(message.chat.id) == str(adminID):
        send_main_menu()
    
    elif message.text[:2] == "KZ" and str(message.chat.id) == str(adminID):
        bot.send_message(godID, "Начал проверку ШПИ: " + message.text)
        pus_data(message.text)

    elif message.text == "Посылка в роботе" and str(message.chat.id) == str(adminID):
        bot.send_message(adminID, "Провожу процесс загрузки посылки.")
        with open(datafolder + "db/box.json", 'r') as ff:
            datastore = json.load(ff)
            status, info = income(datastore["spi"])
            if status[0] == "E":
                bot.send_message(adminID, "ПУС отправил следующую ошибку: " + info)
                send_main_menu()
            else:
                bot.send_message(godID, "Положила в робота посылку.")
                responce = "Выберите направление."
                markup = ReplyKeyboardMarkup()
                markup.row_width = 1
                markup.add(KeyboardButton('Направление: Astana Hub'), \
                    KeyboardButton("Направление: Mega Silkway"), \
                        KeyboardButton("Направление: AIFC"))
                bot.send_message(adminID, responce, reply_markup = markup)

    elif message.text == "Спать" and str(message.chat.id) == str(adminID):
        bot.send_message(godID, "Отправлен спать")
        send_main_menu()
    
    elif message.text[:13] == "Направление: " and str(message.chat.id) == str(adminID):
        address = message.text[13:]
        with open(datafolder + "db/box.json", 'r') as ff:
            datastore = json.load(ff)
            datastore["address"] = address
            with open(datafolder + "db/box.json", 'w') as ff2:
                json.dump(datastore, ff2)
            markup = ReplyKeyboardMarkup()
            markup.row_width = 1
            markup.add(KeyboardButton('GOD: Доехал'), KeyboardButton("GOD: Трабл на дороге"))
            bot.send_message(godID, "Выезжай на точку: " + address, reply_markup=markup)
            bot.send_message(adminID, "Я направляюсь на точку: " + address)
            bot.send_sticker(datastore["id"], "CAADAgADEwEAAtrHBgABeuVsifwYcG4WBA")
            bot.send_message(datastore["id"], "Я выехала доставить Вам посылку [ШПИ №" + \
                datastore["spi"] + "]. Через 15 минут ожидайте меня по адресу: " + \
                    datastore["address"] + ".")
            bot.send_location(datastore["id"], points[address][0], points[address][1])
    
    elif message.text == "Получить посылку":
        with open(datafolder + "db/box.json", 'r') as ff:
            datastore = json.load(ff)
        if str(datastore["id"]) == str(message.chat.id):
            status, info = given(datastore["spi"])
            bot.send_message(adminID, info)
            bot.send_sticker(message.chat.id, "CAADAgADKgEAAtrHBgABFMqO3SCCTN4WBA")
            bot.send_message(message.chat.id, """\
Отлично!
Спасибо, что воспользовались нашей доставкой!
Пожалуйста, не забудьте закрыть крышку за собой.\
""")
            markup = ReplyKeyboardMarkup()
            markup.row_width = 1
            markup.add(KeyboardButton('GOD: Домой'))
            bot.send_message(godID, "Открой крышку. Потом езжай домой.", reply_markup=markup)
    
    elif message.text == "GOD: Домой" and str(message.chat.id) == str(godID):
        markup = ReplyKeyboardMarkup()
        markup.row_width = 1
        markup.add(KeyboardButton('GOD: Пустой'), KeyboardButton('GOD: Не пустой'))
        bot.send_message(godID, "Приехал, нажми.", reply_markup=markup)
    
    elif message.text == "GOD: Пустой" and str(message.chat.id) == str(godID):
        markup = ReplyKeyboardMarkup()
        markup.row_width = 1
        markup.add(KeyboardButton('Спать'))
        bot.send_message(adminID, "Вернулась домой, отдала посылку. Хочу спать.", reply_markup=markup)
        bot.send_message(godID, "Ок, иди отдыхать.")
    
    elif message.text == "GOD: Не пустой" and str(message.chat.id) == str(godID):
        markup = ReplyKeyboardMarkup()
        markup.row_width = 1
        markup.add(KeyboardButton('Вернуть посылку'))
        bot.send_message(adminID, "Вернулась домой, не отдала посылку.", reply_markup=markup)
        bot.send_message(godID, "Жди команды открыть дверь.")
    
    elif message.text == "Вернуть посылку" and str(message.chat.id) == str(adminID):
        with open(datafolder + "db/box.json", 'r') as ff:
            datastore = json.load(ff)
        status, info = back(datastore["spi"])
        bot.send_message(adminID, info)
        bot.send_message(godID, "Открывай")
        bot.send_message(adminID, "Открыла дверь, до свидания!")
    
    elif message.text[:5] == "GOD: " and str(message.chat.id) == str(godID):
        if message.text[-6:] == "Доехал":
            with open(datafolder + "db/box.json", 'r') as ff:
                datastore = json.load(ff)
            markup = ReplyKeyboardMarkup()
            markup.row_width = 1
            markup.add(KeyboardButton('GOD: Домой'))
            bot.send_message(godID, "Ок, жди 30 минут. \
                Если никто не придет, запускай дорогу домой", reply_markup=markup)
            bot.send_message(adminID, "Доехала. Жду 30 минут клиента.")
            bot.send_sticker(datastore["id"], "CAADAgADDwEAAtrHBgABtT_ofg7UMK4WBA")
            markup = ReplyKeyboardMarkup()
            markup.row_width = 1
            markup.add(KeyboardButton('Получить посылку'), KeyboardButton("Я не приду"))
            waiting = datetime.datetime.now() + datetime.timedelta(minutes=30)
            bot.send_message(datastore["id"], "Я приехала. \
Буду ожидать Вас до " + waiting.strftime("%H:%M:%S") +\
"""\
. Когда будете готовы, нажмите 'Получить посылку'. 
Если у Вас не получается забрать ее, нажмите 'Я не приду'.\
""" , reply_markup=markup)
    
    

@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    phone = message.contact.phone_number
    fname = message.contact.first_name
    sname = message.contact.last_name
    user_id = message.contact.user_id
    username = message.chat.username
    logging.info("New user: " + str([phone, fname, sname, user_id, username]))
    add_new_user(phone, user_id)
    bot.send_sticker(message.chat.id, "CAADAgADKgEAAtrHBgABFMqO3SCCTN4WBA")
    bot.send_message(message.chat.id, """\
Отлично!
Теперь, когда Вам будет выслана посылка через меня, я отправлю Вам уведомление.
Вам нужно будет только подойти ко мне и нажать на кнопку "Получить".\
""")


send_main_menu()
bot.polling()
