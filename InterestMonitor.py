from tkinter import *
import cv2
import numpy as np
from PIL import ImageGrab
from PIL import Image, ImageTk

####################################
# customize these functions
####################################

def init(data):
    # load data.xyz as appropriate
    data.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    data.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
    data.screen = ImageGrab.grab(bbox=(0,0,1366,768))
    data.screen_np = np.array(data.screen)
    data.frame = cv2.cvtColor(data.screen_np, cv2.COLOR_BGR2RGB)
    data.frameTk = Image.fromarray(data.frame)
    data.frameTk = ImageTk.PhotoImage(image = data.frameTk)
    data.faces = data.face_cascade.detectMultiScale(data.frame)
    data.cap = cv2.VideoCapture(0)
    data.fail = [False for _ in range(50)]
    data.timerCount = [0 for _ in range(50)]
    data.eyeCount = [0 for _ in range(50)]
    data.facesRead = False
    data.crop = None
    data.resized = False
    data.error = [False for _ in range(50)]
    data.errorCoords = [None for _ in range(50)]
    data.errorColor = (255,0,0)
    data.color = (0,0,0)
    data.change = [False for _ in range(50)]
    data.locked = False

def mousePressed(event, data):
    # use event.x and event.y
    pass

def keyPressed(event, data):
    # use event.char and event.keysym
    if(event.keysym == "space"):
        data.facesRead = True

def timerFired(data):

    data.screen = ImageGrab.grab(bbox=(0,0,1366,768))
    data.screen_np = np.array(data.screen)
    data.frame = data.screen_np

    data.frame = cv2.resize(data.frame, (683, 384))

    if(data.facesRead == True):
        if(data.locked == False):
            data.faces = data.face_cascade.detectMultiScale(data.frame)
            data.eyeCount = [0]*50
            data.locked = True

        for (x, y, w, h) in data.faces:
            data.eyeCount = [0] * 50
            i = 0
            cv2.rectangle(data.frame, (x, y), (x+w, y+h), (0, 0, 0), 2)

            eyes = data.eye_cascade.detectMultiScale(data.frame, 1.05, 1)

            for (a,b,c,d) in eyes:
                if(x < a < x+w and y < b < y+h and x < a+c < x+w and y < b+d < y+h and data.eyeCount[i] < 2 and y < b < (2*y+h)/2):
                    data.eyeCount[i] += 1
                    cv2.rectangle(data.frame, (a,b), (a+c, b+d), (0,0,0), 2)

                    if(data.eyeCount[i] == 2):
                        data.fail[i] = False
                        data.timerCount[i] = 0

            if(data.eyeCount[i] < 2):
                cv2.putText(data.frame, "Not Paying Attention", (x, y - 5), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, data.color, 2, cv2.LINE_AA)
                data.fail[i] = True
            i += 1

    data.frameTk = Image.fromarray(data.frame)
    data.frameTk = ImageTk.PhotoImage(image = data.frameTk)

def timerAttention(data):
    for i in range(len(data.fail)):
        if(data.fail[i] == True):
            try:
                data.timerCount[i] += 1
            except:
                break

    for i in range(len(data.timerCount)):
        if(data.fail[i] == True and data.timerCount[i] >= 50):
            data.error[i] = True
            data.errorCoords[i] = data.faces[i]

def redrawAll(canvas, data):
    # draw in canvas
    canvas.create_image(0, 0, anchor=NW, image=data.frameTk)

    for i in range(len(data.errorCoords)):

        if(data.error[i] == True):
            canvas.create_rectangle(data.errorCoords[i][0], data.errorCoords[i][1], data.errorCoords[i][0] + data.errorCoords[i][2], data.errorCoords[i][1] + data.errorCoords[i][3], outline = "red", width = 5)
            data.change[i] = True
        else:
            break

####################################
# use the run function as-is
####################################

def run(width=300, height=300):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, data.width, data.height,
                                fill='white', width=0)
        redrawAll(canvas, data)
        canvas.update()

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        timerAttention(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 0 # milliseconds
    root = Tk()
    root.resizable(width=False, height=False) # prevents resizing window
    init(data)
    # create the root and the canvas
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.configure(bd=0, highlightthickness=0)
    canvas.pack()
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

run(683, 384)
