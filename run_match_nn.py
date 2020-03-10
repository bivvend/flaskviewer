import numpy as np
import sys
import cv2
import time
import os
import math
from tensorflow.keras.backend import clear_session
from tensorflow.keras import models
from tensorflow.keras import optimizers
from tensorflow.keras.models import model_from_json, load_model


def load_nn():
	#loaded_model = load_model("final_model.h5")
	#loaded_model.compile(loss='mse',     #mean_squared_error 
	#optimizer=optimizers.Adam(lr=2e-5),
	#metrics=['acc'])
	#print("Loaded model from disk")
	loaded_model = None
	return loaded_model	
	
def process_images(image_list, model):
    #im_path ='/software/flaskviewer/static/Images'
	main_start = time.time()   
	IMAGE_DIM_X = 256
	IMAGE_DIM_Y = 256
	for f,im in image_list:
		start = time.time()
		print("Processing {0}".format(f))
		img = cv2.cvtColor(im, cv2.COLOR_RGB2GRAY)
		img = cv2.resize(img,(IMAGE_DIM_X,IMAGE_DIM_Y))
		img = np.reshape(img,[1,IMAGE_DIM_Y,IMAGE_DIM_X,1])
		img = np.array(img, dtype=np.float64) 
		img = img/255.0
		value = 0
		value = model.predict(img)[0][0]
		print("NN output value = {0}".format(value))
		end = time.time() 
		print(round(end - start, 3))  

	clear_session()
		 

    
