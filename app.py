#!/usr/bin/env python
#external imports
from importlib import import_module
import os
import sys
import time
import socket
import argparse
from yattag import Doc

#Flask imports
from flask import Flask, jsonify, render_template, Response, redirect, flash, session, url_for, send_file, make_response
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import Form
from wtforms import StringField, SubmitField,FileField, IntegerField, FloatField, BooleanField
from werkzeug.utils import secure_filename
from wtforms.validators import Required

#internal imports
from pq12_actuator import PQ12actuator
from stepper_controller import StepperController
from run_match import process_images


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

act = "USE_ACTUATOR"
stepper_motor = "USE_STEPPER"

debug = "USE_DEBUG"
overwrite = "OVERWRITE"

motion = stepper_motor
saving = overwrite


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
    
@app.route('/gallery')
def gallery():
    """Image browse page"""
    return render_template('gallery.html') 

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
    '''Runs the lucky imaging cycle'''
    run_actuator_cycle()
    return jsonify(result = "RAN_OK")
    
@app.route('/run_processing', methods = ['GET'])
def run_processing():
    '''Runs the lucky imaging processing'''
    run_image_processing()
    return jsonify(result = "RAN_OK")   
    
@app.route('/step_plus', methods = ['GET'])
def step_plus():
    '''advance stepper motor'''
    count = stepper.make_step(1, True)
    return jsonify(result = str(count))  
    
@app.route('/step_home', methods = ['GET'])
def step_home():
    '''home stepper motor'''
    stepper.home()
    count = stepper.get_count()
    return jsonify(result = str(count))  
    
@app.route('/step_minus', methods = ['GET'])
def step_minus():
    '''advance stepper motor'''
    count = stepper.make_step(1, False)
    return jsonify(result = str(count)) 
    
@app.route('/gallery_refresh', methods = ['GET'])
def gallery_refresh():
    '''Return the html for the gallery wrapper'''    
    return make_gallery_html();
    
@app.route('/best_gallery_refresh', methods = ['GET'])
def best_gallery_refresh():
    '''Return the html for the gallery wrapper'''    
    return make_best_gallery_html();

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
               
def run_image_processing():
    
    if saving == debug:
        print("DEBUG: Loading images from file")
        start = time.time()
        main_camera.load_images_to_buffers(app.config['BITMAP_SAVE_FOLDER'])
        end = time.time()
        print("{0} images loaded in {1} seconds".format(len(main_camera.image_buffer_list), round(end - start, 3)))
   
    process_images(main_camera.image_buffer_list, app.config['BITMAP_SAVE_FOLDER'])
               
def run_actuator_cycle():
    print("Running linear motion cycle")
    main_camera.clear_buffers()
    
    if motion != debug:
        stepper.home()
        main_camera.set_running_state(False, True) #start grabbing to series
    if motion == act:
        lin_acc.set_duty(0.1)
        time.sleep(2)
        lin_acc.set_duty(0.8)
        time.sleep(7)
        lin_acc.set_duty(0.1)
        time.sleep(5)
    if motion == stepper_motor:
        print("Running stepper cycle")        
        stepper.move_to_count(70)
        stepper.home()
    if motion != debug:
        main_camera.set_running_state(True, False) # stop grabbing 
    if motion == act:
        lin_acc.stop() 
    if saving == debug:
        delete = False
    else:
        delete = True
    main_camera.save_buffers(app.config['BITMAP_SAVE_FOLDER'], delete)  
    
def make_gallery_html():
    doc, tag, text = Doc().tagtext()
    with tag('div', klass = 'galleria'): 
        for file in os.listdir(app.config['BITMAP_SAVE_FOLDER']):
            if ".jpg" in file:
                doc.stag('img', src = os.path.join(app.config['BITMAP_SAVE_FOLDER'], file + "?t=" + str(time.time())))       
        
    return(doc.getvalue())  
    
def make_best_gallery_html():
    doc, tag, text = Doc().tagtext()
    with tag('div', klass = 'galleriaBest'): 
        for file in os.listdir(app.config['BITMAP_SAVE_FOLDER']):
            if ".jpg" in file and "best" in file:
                doc.stag('img', src = os.path.join(app.config['BITMAP_SAVE_FOLDER'], file + "?t=" + str(time.time())))       
        
    return(doc.getvalue())  
    

##MAIN
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('cam', help="system, picam or simulated.")
    parser.add_argument('addr', help ="IP Address of server e.g. 0.0.0.0 or hostip for servers own ip")
    args = parser.parse_args()   
    stepper = None
    if motion == act:
        #Setup Actuator
        print("Setting up linear actuator")
        lin_acc = PQ12actuator(18, 1000, 0)
        lin_acc.start() # setup
        lin_acc.stop() #set duty and freq to zero
    if motion == stepper_motor:
        print("Setting up stepper motor")
        stepper = StepperController([29,31,33,35])
        pass
    if motion == debug:
        print("Using simulated motion")
        
    #import camera driver
    if args.cam == 'system':
        print("Using webcam")
        from camera_opencv import Camera
    elif args.cam == 'picam':
        # Raspberry Pi camera module (requires picamera package)
        print("Using Raspberry Pi Camera.")
        from camera_pi import Camera
    elif args.cam == 'simulated':    
        from camera import Camera
        print("Using simulated camera")
    else:
        from camera import Camera
        print("Using simulated camera")
    print(args.addr)

    #Setup camera
    if stepper is None:
        stepper = StepperController([29,31,33,35])
    main_camera = Camera(stepper)
    main_camera.set_save_location(app.config['STATIC_FOLDER'] + '/output.jpg')
    
    
    try:
        if args.addr == "hostip":        
            app.run(host = get_ip(), port=5000, threaded=True)
        else:
            app.run(host = args.addr, port=5000, threaded=True)
    except Exception as e:
        print(e)
        
        #stepper.clean_up()    
    #stepper.clean_up()

    
