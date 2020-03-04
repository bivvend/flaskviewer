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

from run_match_nn import process_images, load_nn


#Camera feed apdapted from https://github.com/miguelgrinberg/flask-video-streaming

app = Flask(__name__)
bootstrap = Bootstrap(app)
moment = Moment(app)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['STATIC_FOLDER'] = 'static'
BITMAP_SAVE_FOLDER = 'static/Images'
app.config['BITMAP_SAVE_FOLDER']= BITMAP_SAVE_FOLDER
loaded_model = None #NN model
#Changed to single camera object and thread.
main_camera = None

debug = "USE_DEBUG"
overwrite = "OVERWRITE"
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
    '''Runs the focus cycle''' 
    main_camera.clear_buffers()
    main_camera.set_running_state(False, True)
    for i in range(0,24):
        main_camera.set_focal_position(i)
        time.sleep(0.5)   
    main_camera.set_running_state(True, False)
    if saving == debug:
        delete = False
    else:
        delete = True
    main_camera.save_buffers(app.config['BITMAP_SAVE_FOLDER'], delete)
    return jsonify(result = "RAN_OK")
    
@app.route('/run_processing', methods = ['GET'])
def run_processing():
    '''Runs the lucky imaging processing'''
    run_image_processing()
    return jsonify(result = "RAN_OK")   
    
@app.route('/step_plus', methods = ['GET'])
def step_plus():
    '''advance focus'''
    main_camera.step_focal_position(1)
    return jsonify(result = str(main_camera.get_focal_position()))  
    
@app.route('/step_home', methods = ['GET'])
def step_home():    
    '''home focus'''
    main_camera.set_focal_position(0)
    return jsonify(result = str(main_camera.get_focal_position())) 
    
@app.route('/step_minus', methods = ['GET'])
def step_minus():
    '''retract focus'''
    main_camera.step_focal_position(-1)
    return jsonify(result = str(main_camera.get_focal_position())) 
    
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
   
    process_images(main_camera.image_buffer_list, loaded_model)
               
    
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
    parser.add_argument('addr', help ="IP Address of server e.g. 0.0.0.0 or hostip for servers own ip")
    args = parser.parse_args()   

       
    #import camera driver
    from camera_opencv import Camera

    #Setup camera
    main_camera = Camera()
    main_camera.set_save_location(app.config['STATIC_FOLDER'] + '/output.jpg')
    
    #load nn
    loaded_model = load_nn()
    
    try:
        if args.addr == "hostip":        
            app.run(host = get_ip(), port=5000, threaded=True)
        else:
            app.run(host = args.addr, port=5000, threaded=True)
    except Exception as e:
        print(e)
        
        #stepper.clean_up()    
    #stepper.clean_up()

    
