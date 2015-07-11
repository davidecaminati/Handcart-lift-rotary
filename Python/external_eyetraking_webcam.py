# Detection of simple eye movement using Raspberry PI 2 and a cheap webcam
# developed based on example by Adrian Rosebrock (http://www.pyimagesearch.com/author/adrian/)
# writed by Davide Caminati 11/07/2015 (http://caminatidavide.it/)
# License GNU GPLv2

# USAGE
# python external_eyetraking_webcam.py -o True

# import the necessary packages
from pyimagesearch.eyetracker_no_face import Eyetracker_no_face
from pyimagesearch import imutils
import argparse
import time
import cv2

# TODO 
# add parameter for video file, camera or raspicam
# read the camera resolution capability and save into an array
# moltiplicator must be connected with effective resolution change from FirstFase and SecondFase proportions
# FirstFase must identify correctly the eye position (no false positive)
# add recognition procerute (hug, nn, whatelse)
# remove italian words
# test improvement of multi core capability (probably we don't need this)
# provide change of resolution of fase 1 and fase 2 as parameter (think about this)
# create a repository on github


#NOTE
# static_optimization parameter (-o) options:
# True fast performance, 
# False if the subject should change the distance of eye to the webcam during initial calibration (fase 1 and 2)


# --- the code start here ---

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", required = False,
	help = "path to the video file, camera or raspicam")
ap.add_argument("-o", "--static_optimization", required = True,
	help = "True if you want static optimization")
args = vars(ap.parse_args())

video_source = args["video"]
usa_ottimizzazione_statica = (args["static_optimization"] == "True")

# find video source (TODO)
if video_source == "raspicam":
    #use Raspicam as video grabber
    pass
elif video_source == "camera": 
    # default setting
    pass
else:
    # load the video file
    pass


# initialize the camera and grab a reference to the raw camera capture

#camera = PiCamera()
#camera.resolution = (640, 480)
#camera.framerate = 32
#rawCapture = PiRGBArray(camera, size=(640, 480))

# construct the eye tracker and allow the camera to worm up
et = Eyetracker_no_face("cascades/haarcascade_eye.xml")
time.sleep(0.1)

# capture frames from the webcam
video_src = 0 # 0 = first webcam /dev/video0
camera = cv2.VideoCapture(video_src)
resolutions = ["high","mid","low","verylow"]

resolution = resolutions.index("low")

#    list of possible resolution to test with the camera
#    160.0 x 120.0
#    176.0 x 144.0
#    320.0 x 240.0
#    352.0 x 288.0
#    640.0 x 480.0
#    1024.0 x 768.0
#    1280.0 x 960.0
#    1280.0 x 1024.0
#

if resolution == 0:
    camera.set(3,1280)
    camera.set(4,960)
    
if resolution == 1:
    camera.set(3,640)
    camera.set(4,480)


if resolution == 2:
    camera.set(3,320)
    camera.set(4,240)
    
if resolution == 3:
    camera.set(3,160)
    camera.set(4,120)
    
number = 0
r0 = 0
r1 = 0
r2 = 0
r3 = 0


# debug
print "fase 1 started"

while number<10:

    start = time.time()

    (grabbed, frame) = camera.read()
    # grab the raw NumPy array representing the image
    
    # check to see if we have reached the end of the
    # video
    if not grabbed:
        break
    
    # resize the frame and convert it to grayscale
    #frame = imutils.resize(frame, width = 300)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # detect eyes in the image
    rects = et.track(gray)
    
    # loop over the eyes bounding boxes and draw them
    for rect in rects:
        cv2.rectangle(frame, (rect[0], rect[1]), (rect[2], rect[3]), (0, 255, 0), 2)
        r0 = rect[0]
        r1 = rect[1]
        r2 = rect[2]
        r3 = rect[3]
        number += 1
    
    # show the tracked eyes , then clear the
    # frame in preparation for the next frame
    cv2.imshow("Tracking", frame)
    #rawCapture.truncate(0)
    
    # calcolate performance
    end = time.time()
    print end - start
    
    # if the 'q' key is pressed, stop the loop
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
# debug
print "fase 1 ended"

#release the camera for change resolution for fase 2
#camera.release()

#wait the camera stop
time.sleep(1)

#rstart camera
#camera = cv2.VideoCapture(0)

resolution2 = resolutions.index("low")

if resolution2 == 0:
    camera.set(3,1280)
    camera.set(4,960)
    
if resolution2 == 1:
    camera.set(3,640)
    camera.set(4,480)


if resolution2 == 2:
    camera.set(3,320)
    camera.set(4,240)
    
if resolution2 == 3:
    camera.set(3,160)
    camera.set(4,120)
    
min_rect = r2/3*2
old_end = 1.0
old_number = number
ottimizzato = 0
best_minrect_array = [0] * 500

print "fase 2 started"

while number<100:
    start = time.time()
    (grabbed, image) = camera.read()
    # grab the raw NumPy array representing the image
    
    # check to see if we have reached the end of the
    # video
    if not grabbed:
        print "break 2"
        break
    #frame = image[r0:r2 , r1:r3]
    #frame = image[r0:r2 , r1:r3]
    tollerance = 0.5
    moltiplicator = 1
    rr0 = int(r0*(1-tollerance)) * moltiplicator
    rr1 = int(r1*(1-tollerance)) * moltiplicator
    rr2 = int(r2*(1+tollerance)) * moltiplicator
    rr3 = int(r3*(1+tollerance)) * moltiplicator
    #print "ok",r0,r1,r2,r3
    
    frame = image[rr1:rr3 , rr0:rr2]
    # resize the frame and convert it to grayscale
    #frame = imutils.resize(frame, width = 300)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # detect eyes in the image
    rects = et.track(gray,(min_rect,min_rect))
    
    # loop over the face bounding boxes and draw them
    for rect in rects:
        cv2.rectangle(frame, (rect[0], rect[1]), (rect[2], rect[3]), (0, 255, 0), 2)
        number += 1
        print number
        # save the current min_rect value into the array 
        best_minrect_array[min_rect] = int (best_minrect_array[min_rect]) +1 
    
    # show the tracked eyes and face, then clear the
    # frame in preparation for the next frame

    cv2.imshow("Eye Tracking", frame)
    #rawCapture.truncate(0)
    end = time.time()
    elapsed_time = end - start
    if usa_ottimizzazione_statica:
        # static optimization
        if (elapsed_time < old_end) & (old_number <> number) :
            if ottimizzato < 50 :
                ottimizzato +=1
                min_rect +=int(min_rect/100*10) +3
                
        else:
            if ottimizzato < 50:
                min_rect -=int(min_rect/100*10) +3
        # after last update take some margin and fix the value of min_rect for future recognition    
        if ottimizzato == 49:
            min_rect -= int(min_rect*5/100)
            ottimizzato = 1000
    else:
        # dinamic optimization
        if (elapsed_time < old_end) & (old_number <> number) :
            min_rect +=3
        else:
            min_rect -=6
            
    print elapsed_time,min_rect
    old_end = end
    old_number = number
    if min_rect < 10:
        print "min_rect too small "
        break
    if min_rect > 600:
        print "min_rect too large"
        break
    # if the 'q' key is pressed, stop the loop
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

print "fase 2 ended"
print best_minrect_array
number_of_good_min_rect = max(best_minrect_array)
print number_of_good_min_rect
best_min_rect = best_minrect_array.index(number_of_good_min_rect)
print best_min_rect

# release resource unnecessary
best_minrect_array = []

if number_of_good_min_rect > 25:
    #now i have a good reason to use best_min_rect as my min_rect
    print "fase 3 started"
    
    #setting of all the variable
    min_rect = best_min_rect
    tollerance = 0.5
    moltiplicator = 1
    rr0 = int(r0*(1-tollerance)) * moltiplicator
    rr1 = int(r1*(1-tollerance)) * moltiplicator
    rr2 = int(r2*(1+tollerance)) * moltiplicator
    rr3 = int(r3*(1+tollerance)) * moltiplicator
    while True:
        
        start = time.time()
        (grabbed, image) = camera.read()
        
        # check to see if we have reached the end of the
        # video
        if not grabbed:
            print "break 3"
            break

        frame = image[rr1:rr3 , rr0:rr2]
        # resize the frame and convert it to grayscale
        #frame = imutils.resize(frame, width = 300)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # detect eyes in the image
        rects = et.track(gray,(min_rect,min_rect))
        
        # loop over the face bounding boxes and draw them
        for rect in rects:
            cv2.rectangle(frame, (rect[0], rect[1]), (rect[2], rect[3]), (0, 255, 0), 2)
            print "eye located"

        # show the tracked eyes
        cv2.imshow("Eye Tracking", frame)
        #rawCapture.truncate(0)
        end = time.time()
        elapsed_time = end - start
        print elapsed_time
        
        # todo
        # find where you still looking (right, left, center)
        
        
        # if the 'q' key is pressed, stop the loop
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

camera.release()
cv2.destroyAllWindows()