#!/usr/bin/env python
from importlib import import_module
import os
import os
import sys

#Flask imports
from flask import Flask, render_template, Response, redirect, flash, session, url_for, send_file, make_response
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import Form
from wtforms import StringField, SubmitField,FileField, IntegerField, FloatField, BooleanField
from werkzeug.utils import secure_filename
from wtforms.validators import Required
import argparse


#Camera feed apdapted from https://github.com/miguelgrinberg/flask-video-streaming

app = Flask(__name__)
bootstrap = Bootstrap(app)
moment = Moment(app)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['STATIC_FOLDER'] = 'static'
UPLOAD_FOLDER = '//TEST'
BITMAP_SAVE_FOLDER = '//TEST'
app.config['UPLOAD_FOLDER']= UPLOAD_FOLDER
app.config['BITMAP_SAVE_FOLDER']= BITMAP_SAVE_FOLDER


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('main.html') #was index.html


def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('cam', help="system, picam or simulated.")
    parser.add_argument('addr', help ="IP Address of server e.g. 0.0.0.0")
    args = parser.parse_args()   

        #import camera driver
    if args.cam == 'system':
        if os.environ.get('CAMERA'):
            print("Using system camera")
            Camera = import_module('camera_' + os.environ['CAMERA']).Camera
        else:
            print("Using simulated camera")
            from camera import Camera
    elif args.cam == 'picam':
        # Raspberry Pi camera module (requires picamera package)
        from camera_pi import Camera
    elif args.cam == 'simualted':    
        from camera_pi import Camera
        print("Using simulated camera")
    else:
        from camera import Camera
        print("Using simulated camera")
    print(args.addr)
    app.run(host = args.addr, port=5000, threaded=True)
