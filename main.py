import socket
import threading
import logging
import datetime
import time
# import RPi.GPIO as GPIO


# GPIO.setmode(GPIO.BCM)
# GPIO.setwarnings(False)
pins = [18,17,15,14]
# GPIO.setup(pins, GPIO.OUT)

lock = threading.Lock()
last_command = datetime.datetime.now()
pause = 400000


logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)-15s]:(%(threadName)-10s) %(message)s'
)


def move(dir):
    if dir == "w":
        logging.debug("Moving forward")
    elif dir == "s":
        logging.debug("Moving backward")
    elif dir == "d":
        logging.debug("Turning right")
    elif dir == "a":
        logging.debug("Turning left")
    elif dir == "o":
        logging.debug("Open door")
    elif dir == "l":
        logging.debug("Light up")
    elif dir == "k":
        logging.debug("Light down")


def stop():
    logging.debug("Stopping all motors")


def check_handler():
    logging.debug("Checker thread started")
    while True:
        time.sleep(0.1)
        now = datetime.datetime.now()
        delta = now - last_command
        if delta.microseconds > pause:
            stop()


def client_handler(sock: socket.socket, address: str, port: int) -> None:
    while True:
        try:
            global last_command
            message = sock.recv(1024)
            # logging.debug("Recv: {message} from {address}:{port}")
            lock.acquire()
            last_command = datetime.datetime.now()
            lock.release()
            move(message.decode("utf-8").strip("\n"))
            # logging.debug("Changed last command")
        except OSError:
            break

        if len(message) == 0:
            break

        # sent_message = message
        # while True:
        #     sent_len = sock.send(sent_message)
        #     if sent_len == len(sent_message):
        #         break
        #     sent_message = sent_message[sent_len:]
        # logging.debug("Send: {message} to {address}:{port}")
    sock.close()
    logging.debug("Bye-bye: {address}:{port}")


def main(host: str = '::', port: int = 7777) -> None:
    serversocket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
    serversocket.bind((host, port))
    serversocket.listen(128)
    socket.setdefaulttimeout(120)

    checker_thread = threading.Thread(target=check_handler)
    checker_thread.daemon = True
    checker_thread.start()

    # print("Starting TCP Echo Server at {host}:{port}")
    try:
        while True:
            clientsocket, (client_address, client_port) = serversocket.accept()
            logging.debug("New client: {client_address}:{client_port}")
            client_thread = threading.Thread(
                target=client_handler,
                args=(clientsocket, client_address, client_port))
            client_thread.daemon = True
            client_thread.start()
    except KeyboardInterrupt:
        print("Shutting down")
    finally:
        serversocket.close()


if __name__ == "__main__":
    main()

