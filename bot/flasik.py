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
import threading
from flask import Flask, render_template, request, Markup, jsonify


logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)-15s] by %(threadName)s: %(message)s'
)

datafolder = os.path.abspath(__file__).split("flasik.py")[0]

TELEGRAM_TOKEN = '942402785:AAHdH7jhutO_dge_4DKa1jWGemXAI5SrZHY'

bot = telebot.TeleBot(TELEGRAM_TOKEN)

adminID = "-1001286114767"
godID = "-323859236"

points = {"Astana Hub": ["51.088513", "71.413808"], \
    "Mega Silkway": ["51.088769" ,"71.411976"], \
        "AIFC": ["51.087676", "71.414830"]}


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        passcodenew = request.form['passcode']
        logging.info("given pin from web is: " + str(passcodenew))
        with open(datafolder + "db/box.json", 'r') as ff:
            datastore = json.load(ff)
            pincode = datastore["pin"][0]
            logging.info("real pin is: " + str(pincode))
            if str(pincode) == str(passcodenew):
                alert = "Не забудьте закрыть крышку, пожалуйста."
                bot.send_message(godID, "Открывай")
                return render_template(
                    "index.html", **locals())
            else:
                alert = "Вы ввели неправильный пароль"
                return render_template(
                    "index.html", **locals())
    alert = "Введите пароль из смс, пожалуйста"
    return render_template('index.html', **locals())


# POLLING = threading.Thread(target=bot_polling)
# POLLING.daemon = True
# POLLING.start()


if __name__ == "__main__":
    # BOT = threading.Thread(target=botting)
    # BOT.start()
    # app.run(host='0.0.0.0', debug=True)
    # bot.polling()
    # send_main_menu()
    app.run(host='0.0.0.0', debug=True)
