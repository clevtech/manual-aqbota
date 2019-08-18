#!/usr/bin/env python

from flask import Flask, render_template, Response, jsonify
import sys
try:
    import cv2
except:
    sys.path.insert(0, "/opt/ros/kinetic/lib/python2.7/dist-packages/")
import socket
import logging
import time

IP = "rpi3"
port = 7777

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)-15s]: %(message)s'
)


def init_client():
    sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    server_address = (IP, port)
    while True:
        try:    
            sock.connect(server_address)
            break
        except Exception as e:
            logging.debug('Connection error is: {}'.format(e))
            sock.close()
            sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            logging.debug('No connection to {} port {}'.format(*server_address))
            time.sleep(2)
    logging.debug('Connected to {} port {}'.format(*server_address))
    return sock

def motion(key):
    global sock
    try:
        sock.sendall(key.encode())
    except:
        logging.debug("Cannot send data to server, restart client.")
        try:
            sock.close()
            time.sleep(1)
            sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            sock.connect(server_address)
            logging.debug("Connected to server.")
        except:
            pass

class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.flag = self.video.set(cv2.CAP_PROP_FPS, 5)
        self.video.set(cv2.CAP_PROP_FRAME_WIDTH, 160)
        self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, 120)
    def __del__(self):
        self.video.release()
    
    def get_frame(self):
        success, image = self.video.read()
        # grayFrame = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        if success:
            ret, jpeg = cv2.imencode('.jpg', image)
        else:
            jpeg = "none"
        return jpeg.tobytes()

app = Flask(__name__)
sock = init_client()

@app.route('/')
def robcont():
    global sock
    sock = init_client()
    return render_template("control.html")


@app.route('/robot-control/<direction>', methods=['POST'])
def ajax_request(direction):
    direction = str(direction).replace("\n", '').replace("\r", '').replace("/", "")
    motion(direction)
    return jsonify()

@app.route('/video/')
def index():
    return render_template('index.html')

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='::', debug=True)