import cv2
import numpy as np
from PIL import ImageGrab

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
facesRead = False
start = False

while True:
    # Read the frame
    screen = ImageGrab.grab(bbox=None)
    screen_np = np.array(screen)
    frame = cv2.cvtColor(screen_np, cv2.COLOR_BGR2GRAY)

    if(start == False):
        key = cv2.waitKey(30)
        if(key != -1):
            start = True

    if(key != -1):
        if(facesRead == False):
            faces = face_cascade.detectMultiScale(frame, 1.1, 5)
            facesRead = True

        eyeCount = [0]*len(faces)

        for (x, y, w, h) in faces:
            i = 0
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 0), 2)

            eyes = eye_cascade.detectMultiScale(frame, 1.1, 5)
            for (a,b,c,d) in eyes:
                if(x < a < x+w and y < b < y+h and x < a+c < x+w and y < b+d < y+h and eyeCount[i] < len(faces)*2 and y < b < (2*y+h)/2):
                    eyeCount[i] += 1
                    cv2.rectangle(frame, (a,b), (a+c, b+d), (0,0,0), 2)

            if(eyeCount[i] < 2):
                cv2.putText(frame, "Not Paying Attention", (x, y - 5), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0,0,0), 2, cv2.LINE_AA)
            i += 1
            print(eyeCount)

    cv2.imshow('img', frame)

    # Stop if escape key is pressed

    k = cv2.waitKey(30) & 0xff
    if k==ord("q"):
        break

cv2.destroyAllWindows()
