#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import threading
import logging
import datetime
import time
import RPi.GPIO as GPIO

def stop():
    logging.info("Stopping all motors")
    GPIO.output(pins, GPIO.LOW)


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
pins = [27,17,19,26,23,24]
GPIO.setup(pins, GPIO.OUT)
GPIO.output(pins, GPIO.LOW)
stop()

lock = threading.Lock()
last_command = datetime.datetime.now()
pause = 400000


logging.basicConfig(
    level=logging.debug,
    format='[%(asctime)-15s]:(%(threadName)-10s) %(message)s'
)


def move(dir):
    if dir == "w":
        logging.info("Moving forward")
        GPIO.output(17, GPIO.HIGH)
        GPIO.output(27, GPIO.LOW)
        GPIO.output(19, GPIO.HIGH)
        GPIO.output(26, GPIO.LOW)
    elif dir == "s":
        logging.info("Moving backward")
        GPIO.output(27, GPIO.HIGH)
        GPIO.output(17, GPIO.LOW)
        GPIO.output(26, GPIO.HIGH)
        GPIO.output(19, GPIO.LOW)
    elif dir == "d":
        logging.info("Turning right")
        GPIO.output(19, GPIO.HIGH)
        GPIO.output(26, GPIO.LOW)
        GPIO.output(27, GPIO.HIGH)
        GPIO.output(17, GPIO.LOW)
    elif dir == "a":
        logging.info("Turning left")
        GPIO.output(17, GPIO.HIGH)
        GPIO.output(27, GPIO.LOW)
        GPIO.output(26, GPIO.HIGH)
        GPIO.output(19, GPIO.LOW)
    elif dir == "o":
        logging.info("Open door")
        GPIO.output(24, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(24, GPIO.LOW)
    elif dir == "k":
        stop()
    # elif dir == "l":
    # logging.info("Light up")
    # elif dir == "k":
    # logging.info("Light down")


def check_handler():
    logging.info("Checker thread started")
    while True:
        time.sleep(0.1)
        now = datetime.datetime.now()
        delta = now - last_command
        if delta.microseconds > pause:
            stop()


def client_handler(sock: socket.socket, shit: int) -> None:
    while True:
        try:
            global last_command
            message = sock.recv(1024)
            # logging.info("Recv: {message} from {address}:{port}")
            lock.acquire()
            last_command = datetime.datetime.now()
            lock.release()
            move(message.decode("utf-8").strip("\n"))
            # logging.info("Changed last command")
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
        # logging.info("Send: {message} to {address}:{port}")
    sock.close()
    logging.info("Bye-bye")


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
            clientsocket, shit = serversocket.accept()
            logging.info("New client")
            client_thread = threading.Thread(
                target=client_handler,
                args=(clientsocket, 6))
            client_thread.daemon = True
            client_thread.start()
    except KeyboardInterrupt:
        print("Shutting down")
    finally:
        serversocket.close()


if __name__ == "__main__":
    main()

