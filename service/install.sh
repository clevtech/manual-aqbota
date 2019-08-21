#!/bin/bash
cp ./flask.conf /etc/init/flask.conf
echo "Copied flask.conf"
cp ./control.conf /etc/init/control.conf
echo "Copied control.conf"
cp ./flask.service /lib/systemd/system/flask.service
cp ./control.service /lib/systemd/system/control.service
echo "Added all files"
cd ..
chown naboo camera.py
chown naboo main.py
chmod 777 main.py
chmod 777 camera.py
sudo systemctl daemon-reload
echo "Done chown and chmod"
sudo service flask start
sudo service flask enable
sudo service control start
sudo service control enable
echo "Started services"
