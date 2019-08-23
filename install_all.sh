#!/bin/bash
cp commands.sh ~/.commands.sh && chmod 777 ~/.commands.sh
sudo apt install sshpass curl
curl -O https://raw.githubusercontent.com/denilsonsa/prettyping/master/prettyping
sudo mv prettyping /usr/local/bin
sudo chmod +x /usr/local/bin/prettyping
cat bashes.sh >> ~/.bashrc
source ~/.bashrc