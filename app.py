#!/usr/bin/env python
from importlib import import_module
import os
import os
import sys
import time
import socket

#Flask imports
from flask import Flask, jsonify, render_template, Response, redirect, flash, session, url_for, send_file, make_response
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import Form
from wtforms import StringField, SubmitField,FileField, IntegerField, FloatField, BooleanField
from werkzeug.utils import secure_filename
from wtforms.validators import Required
import argparse

from pq12_actuator import PQ12actuator


#Camera feed apdapted from https://github.com/miguelgrinberg/flask-video-streaming

app = Flask(__name__)
bootstrap = Bootstrap(app)
moment = Moment(app)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['STATIC_FOLDER'] = 'static'
BITMAP_SAVE_FOLDER = 'static/Images'
app.config['BITMAP_SAVE_FOLDER']= BITMAP_SAVE_FOLDER

#Changed to single camera object and thread.
main_camera = None


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

# No cacheing at all for API endpoints.
@app.after_request
def add_header(response):
    # response.cache_control.no_store = True
    if 'Cache-Control' not in response.headers:
        response.headers['Cache-Control'] = 'no-store'
    return response
    
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
    """Saves a frame to be displayed on screen - not for processing"""
    if main_camera is not None:
        main_camera.set_save_location(app.config['STATIC_FOLDER'] + '/output.jpg')
        main_camera.set_running_state(False, False)
        #Sleep until a frame has been saved
        time.sleep(1)
        main_camera.set_running_state(True, False)
        main_camera.set_save_location(app.config['BITMAP_SAVE_FOLDER'] + '/output.jpg')
        return jsonify(result = app.config['STATIC_FOLDER'] + '/output.jpg')
    else:
        return jsonify(result = 'NOT_SAVED')
        
@app.route('/run_cycle', methods = ['GET'])
def run_cycle():
    run_actuator_cycle()   
    
    return jsonify(result = "RAN_OK")

##GENERAL FUNCTIONS
def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        #save frame to file
        if not camera.get_running_state():
            print("Saving from app.py")
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
               
def run_actuator_cycle():
    print("Running linear actuator cycle")
    main_camera.clear_buffers()
    main_camera.set_running_state(False, True) #start grabbing to series
    lin_acc.set_duty(0.1)
    time.sleep(2)
    lin_acc.set_duty(0.8)
    time.sleep(5)
    lin_acc.set_duty(0.1)
    time.sleep(5)
    main_camera.set_running_state(True, False) # stop grabbing 
    lin_acc.stop() 
    main_camera.save_buffers(app.config['BITMAP_SAVE_FOLDER'])   
    

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

    #Setup camera
    main_camera = Camera()
    main_camera.set_save_location(app.config['STATIC_FOLDER'] + '/output.jpg')
    
    #Setup Actuator
    lin_acc = PQ12actuator(18, 1000, 0)
    lin_acc.start() # setup
    lin_acc.stop() #set duty and freq to zero

    if args.addr == "hostip":        
        app.run(host = get_ip(), port=5000, threaded=True)
    else:
        app.run(host = args.addr, port=5000, threaded=True)

    
