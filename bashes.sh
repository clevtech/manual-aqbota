alias connectbot='sshpass -p 'The2ndlaw' ssh naboo@rpi3 -p 1994'
alias controlbot='python3 ~/manual-aqbota/client.py'
alias checkbot='prettyping rpi3'
alias botflask="connectbot 'echo The2ndlaw | sudo -S service flask status'"
alias botcontrol="connectbot 'echo The2ndlaw | sudo -S service control status'"
alias restartbot="connectbot 'echo The2ndlaw |sudo -S service control restart && sudo service flask restart'"
alias helpbot="~/.commands.sh"