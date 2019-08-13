import sys
import select
import termios
import tty
import socket
import logging
import time

IP = "192.168.1.149"
port = 7777


settings = termios.tcgetattr(sys.stdin)
msg = """
Reading from the keyboard  and Publishing to aqbota!
---------------------------
Moving around:
      w   
    a s d
---------------------------
o : open door
l : turn on lights
k : turn off lights

CTRL-C to quit
"""

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)-15s]: %(message)s'
)


def getKey():
    tty.setraw(sys.stdin.fileno())
    select.select([sys.stdin], [], [], 0)
    key = sys.stdin.read(1)
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key


def main():
    print(msg)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (IP, port)
    while True:
        try:    
            sock.connect(server_address)
            break
        except Exception as e:
            logging.debug('Connection error is: {}'.format(e))
            sock.close()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            logging.debug('No connection to {} port {}'.format(*server_address))
            time.sleep(2)
    logging.debug('Connected to {} port {}'.format(*server_address))

    while True:
        key = getKey()
        if (key == '\x03'):
            break
        else:
            try:
                sock.sendall(key.encode())
            except:
                logging.debug("Cannot send data to server, restart client.")
                try:
                    sock.close()
                    time.sleep(1)
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect(server_address)
                    logging.debug("Connected to server.")
                except:
                    pass

if __name__=="__main__":
    main()
