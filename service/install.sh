#!/bin/bash
echo "Enter password please:"
sudo -s
cp ./flask.conf /etc/init/flask.conf
cp ./control.conf /etc/init/control.conf
cp ./flask.service /lib/systemd/system/flask.service
cp ./control.service /lib/systemd/system/control.service
echo "Added all files"
cd ..
chown naboo camera.py
chown naboo main.py
chmod 777 main.py
chmod 777 camera.py
echo "Done chown and chmod"
sudo service flask start
sudo service flask enable
sudo service control start
sudo service control enable
echo "Started services"
echo "Flask status:"
sudo service flask status
echo "Control status:"
sudo service control status
