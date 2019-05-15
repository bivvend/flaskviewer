import numpy as np
import cv2
from matplotlib import pyplot as plt
import time
import os
import math
import peakutils
from multiprocessing.dummy import Pool as ThreadPool
#Load all images from dir

im_path ='/home/pi/github/ViewerImages/w2'  

comp_image = 'template_bold.bmp'
comp_im = cv2.imread(comp_image, 0)


# Initiate SIFT detector and BruteForce Matcher 
orb = cv2.ORB_create(edgeThreshold = 10, patchSize = 15)   #Edge threshold reduce for small template
bf = cv2.BFMatcher(cv2.NORM_HAMMING,crossCheck=True)


file_list = os.listdir(im_path)
image_list = []
start = time.time()
for f in file_list:
    if ".jpg" in f:
        image_list.append( (f, cv2.imread(os.path.join(im_path, f),0)))
end = time.time()
print("{0} images loaded in {1} seconds".format(len(image_list), round(end - start, 3)))

main_start = time.time()
#Calculate focal parameter after and blurring to remove HF noise   calculate and store matches for cropping
start = time.time()
val_list = []
matches_list = []
keypoint_list = []

kp1, des1 = orb.detectAndCompute(comp_im,None)

def run_processing(tup):
    f, img = tup
    kp2, des2 = orb.detectAndCompute(img,None)
    pts = cv2.KeyPoint_convert(kp2)    
    matches = bf.match(des2, des1)
    matches = sorted(matches, key = lambda x:x.distance)
    matches_list.append(matches)
    keypoint_list.append(kp2)
    print("Number of matches for image {0} = {1}".format(f, len(matches)))
    if len(img.shape) > 2:
        img_filt = cv2.bilateralFilter(img[:,:,2], 5, 100, 100) ##ADD A FILTER
        val = cv2.Laplacian(img_filt.astype(np.float64)[:,:,2], cv2.CV_64F).var()       
    else:
        img_filt = cv2.bilateralFilter(img[:,:], 5, 100, 100) ##ADD A FILTER
        val = cv2.Laplacian(img_filt.astype(np.float64)[:,:], cv2.CV_64F).var()
    val_list.append(val * (math.sqrt(len(matches)) + 1)) 

use_threads = True

if use_threads:
    pool = ThreadPool(4)
    pool.map(run_processing, image_list)
    pool.close()
    pool.join()
else:
    for tup in image_list:
        run_processing(tup)

end = time.time()
print("{0} images processed in {1} seconds".format(len(image_list), round(end - start, 3)))

#Pick N best using peak fitting
start = time.time()
cb = np.array(val_list)
indices = peakutils.indexes(cb, thres=0.6, min_dist=7)

#Generate a list of files around the peak
good_images = []  #(filename, img) tuple
good_matches = []
good_keypoints = []
range_im = 6
for i in indices:
    if i - range_im > 0 and i + range_im < len(image_list):
        good_images.extend(image_list[i - range_im: i + range_im]) 
        good_matches.extend(matches_list[i - range_im: i + range_im])
        good_keypoints.extend(keypoint_list[i - range_im: i + range_im])
end = time.time()
print("Peaks found at {}".format(indices))
print("{0} images selected in {1} seconds".format(len(good_images), round(end - start, 3)))
print("Match data stored for {0} images".format(len(good_matches)))


# create a CLAHE object 
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(5,5))

all_points = []
    
for f, im in good_images:
    im = clahe.apply(im)    
    kps = good_keypoints[[y[0] for y in good_images].index(f)]
    matches = good_matches[[y[0] for y in good_images].index(f)]                          
    for mat in matches:
        # Get the matching keypoints for each of the images
        img1_idx = mat.queryIdx
        # x - columns
        # y - rows
        # Get the coordinates
        all_points.append(kps[img1_idx].pt)
    
print(len(all_points))

x_sum = 0
y_sum = 0
for pt in all_points:
    x_sum += pt[0]
    y_sum += pt[1]

x_mean = x_sum / len(all_points)
y_mean = y_sum / len(all_points)

print("Mean feature is at ({0},{1})".format(x_mean, y_mean))

clip_size = 400

min_x = int(x_mean - clip_size/2)
min_y = int(y_mean - clip_size/2)

if min_x < 0:
    min_x = 0
if min_y < 0:
    min_y = 0

max_x = int(x_mean + clip_size/2)
max_y = int(y_mean + clip_size/2)

im_shape = good_images[0][1].shape
print(im_shape)

if max_x > im_shape[1] - 1:
    max_x = im_shape[1] - 1
if max_y > im_shape[0] - 1:
    max_y = im_shape[0] - 1

clipped_images = []
for f, im in good_images:
    clip = im[min_y:max_y, min_x: max_x]    
    clip = clahe.apply(clip)    
    clipped_images.append( (f, clip) )
    

#FEATURE MATCHING ON CLIPPED IMAGES

template_im = np.copy(comp_im)
template_im = clahe.apply(template_im)

kp2, des2 = orb.detectAndCompute(template_im,None)
key2 = cv2.drawKeypoints(template_im, kp2, None, color=(0,0,0), flags=0)

best_set = []
for f, im in clipped_images:
    new_im = np.copy(im)
    #new_im = cv2.blur(new_im, (3,3))
    #new_im= clahe.apply(new_im)
    kp1, des1 = orb.detectAndCompute(new_im,None)
    matches = bf.match(des1, des2)
    matches = sorted(matches, key = lambda x:x.distance)
    print("File {0} has {1} matches".format(f, len(matches)))
    best_set.append( (f, len(matches) ) )
#    img3 = cv2.drawMatches(new_im,kp1,template_im,kp2,matches[:10], None, flags=2)
#    plt.imshow(img3)
#    plt.show()
    
best_set = sorted(best_set, key = lambda x:-1*x[1])
main_end = time.time()
print(best_set)

print("Total run time = {0} seconds".format(round(main_end - main_start, 3)))
if len(best_set) > 2:
    for f, img in image_list:
        if best_set[0][0] == f:
            plt.imshow(img, cmap = 'gray')
            plt.show()
        if best_set[1][0] == f:
            plt.imshow(img, cmap = 'gray')
            plt.show()
        if best_set[2][0] == f:
            plt.imshow(img, cmap = 'gray')
            plt.show()
