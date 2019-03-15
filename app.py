#!/usr/bin/env python
from importlib import import_module
import os
import os
import sys
import socket

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
BITMAP_SAVE_FOLDER = '//TEST'
app.config['BITMAP_SAVE_FOLDER']= BITMAP_SAVE_FOLDER

#Changed to single camera object and thread.
main_camera = None
saved_fame = None

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

#ROUTE FUNCTIONS

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('main.html') #was index.html

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(main_camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/save_frame', methods = ['GET'])
def save_frame():
    if main_camera is not None:
        main_camera.save_frame(app.config['STATIC_FOLDER'] + '/last_image.jpg')
        return(app.config['STATIC_FOLDER'] + '/1.jpg')
    else:
        return(app.config['STATIC_FOLDER'] + '/1.jpg')

##GENERAL FUNCTIONS
def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

##MAIN
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('cam', help="system, picam or simulated.")
    parser.add_argument('addr', help ="IP Address of server e.g. 0.0.0.0 or hostip for servers own ip")
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
        print("Using Raspberry Pi Camera.")
        from camera_pi import Camera
    elif args.cam == 'simulated':    
        from camera_pi import Camera
        print("Using simulated camera")
    else:
        from camera import Camera
        print("Using simulated camera")
    print(args.addr)

    main_camera = Camera()


    if args.addr == "hostip":        
        app.run(host = get_ip(), port=5000, threaded=True)
    else:
        app.run(host = args.addr, port=5000, threaded=True)

    