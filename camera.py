from flask import Flask, render_template, Response
import cv2

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
            jpeg = None
        return jpeg.tobytes()

app = Flask(__name__)

@app.route('/')
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