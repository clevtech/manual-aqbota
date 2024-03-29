#!/bin/bash
cp ./flask.conf /etc/init/flask.conf
echo "Copied flask.conf"
cp ./bot.conf /etc/init/bot.conf
echo "Copied control.conf"
cp ./flask.service /lib/systemd/system/flask.service
cp ./bot.service /lib/systemd/system/bot.service
echo "Added all files"
chown $USER flasik.py
chown $USER main.py
chmod 777 main.py
chmod 777 flasik.py
sudo systemctl daemon-reload
echo "Done chown and chmod"
sudo service bot restart && sudo service flask restart
echo "Started services"
