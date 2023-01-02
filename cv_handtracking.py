# -*- coding: utf-8 -*-
import numpy as np
import cv2
import keyboard
import math
from cvzone.HandTrackingModule import HandDetector

# color table 
orange = (0, 69, 255)
light_green = (144, 238, 144)
purple = (128, 0, 128)
pink = (203, 192, 255)

class Btn: # the UI button
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 30
        self.color = (0, 255, 255)
        
    def draw(self, background):
        cv2.ellipse(background, (self.x, self.y), (self.radius, self.radius), 0, 0, 360, self.color, -1)

class FingerTip: # the position of the finger tip (thumb, index_finger, middle_finger, ring_finger, pinky)
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
        
class Clay:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.radius = 40
        self.coords = generate_points(self)
        self.color = color
    def draw(self, background, color):
        """
        rightPoint = (self.x + self.radius if self.x + self.radius <= WIDTH - 1 else WIDTH - 1, self.y)
        leftPoint = (self.x - self.radius if self.x - self.radius > 0 else 0, self.y)
        topPoint = (self.x , self.y - self.radius if self.y - self.radius > 0 else 0)
        buttomPoint = (self.x , self.y + self.radius if self.y + self.radius <= HEIGHT - 1 else HEIGHT - 1)
        """
        if self.coords == []:
            self.coords = generate_points(self)
        points = np.array(self.coords)
        #for coord in self.coords:
        #    points = np.append(points, [[int(coord[0]), int(coord[1])]], 0 )
        cv2.fillConvexPoly(background, points, color)



# parameter
WIDTH, HEIGHT = 640, 360 # 1280, 720
selection = -1
select_mode = 0
counter = 0
object_display = False
clays = []

btn0 = Btn(120, 50)
btn1 = Btn(200, 50)
btn2 = Btn(280, 50)
btn3 = Btn(360, 50)
btn_list = [btn0, btn1, btn2, btn3]
#clay = Clay(200, 250, [], pink)

zeroModePress = False
zerModeDragPoint = []

def drawUI(img):
    for btn in btn_list:
        btn.draw(img)
    

def get_frame(cap):
    success, img = cap.read() # get the frame from webcam
    img = cv2.flip(img, 1)

    fingers = [0,0,0,0,0]

    hands, img = detector.findHands(img)

    drawUI(img)
    
    global object_display
    global zerModeDragPoint
    data = []
    lmList = []
    # gray_img = spotlight(img, data, fingers)
    
    # landmark values - (x, y, z) * 21
    for hand in hands:        
        lmList = hand['lmList']
        for lm in lmList:
            data.extend([lm[0], lm[1], lm[2]]) # reverse y-dir
                
        fingers = detector.fingersUp(hand) # [1, 1, 1, 1, 1] if fingers up
        #print(fingers)
        # print(len(data))
        select_mode = detect_click_btn(img, data, fingers)
        if select_mode == 0:
            #clay.coords = generate_points(clay)
            object_display = True
            showButtonNumber(btn0, "0", img)
            zeroMode(lmList, img)

        elif select_mode == 1:
            candle(img, data, fingers)
            new_img = spotlight(img, data, fingers)
            img = new_img
            showButtonNumber(btn1, "1", img)
        elif select_mode == 2:
            twoFingerMode(lmList, img)
            showButtonNumber(btn2, "2", img)
        elif select_mode == 3:
            showButtonNumber(btn2, "3", img)

        
    if object_display == True:
        for clay in clays:
            clay.draw(img, clay.color)
            #global zeroModeDragPoint
            #print(zerModeDragPoint)
            print(zerModeDragPoint)

        if zerModeDragPoint != []:
            clayID = zerModeDragPoint[0]
            pointID = zerModeDragPoint[1]
            cv2.circle(img, clays[clayID].coords[pointID], 5, (255, 0, 0), cv2.FILLED)

        #for point in zerModeDragPoint:

    cv2.imshow("Image", img)
    cv2.waitKey(1)

def distance(a, b):
    dis = pow((a.x - b.x), 2) + pow(a.y - b.y, 2)
    dis = math.sqrt(dis)
    return dis

def detect_click_btn(img, data, fingers):
    global selection, select_mode, counter
    counterspeed = 8
    index_finger_tip = FingerTip(int(data[24]), int(data[25]))

    if fingers == [0, 1, 0, 0, 0] and distance(index_finger_tip, btn_list[0]) <= btn_list[0].radius: 
        if selection != 0: # ENTER SELECTION 0
            counter = 1
        selection = 0
        # print("selection = 0")
    elif fingers == [0, 1, 0, 0, 0] and distance(index_finger_tip, btn_list[1]) <= btn_list[1].radius :
        if selection != 1: # ENTER SELECTION 1
            counter = 1
        selection = 1
        # print("selection = 1")
    elif fingers == [0, 1, 0, 0, 0] and distance(index_finger_tip, btn_list[2]) <= btn_list[2].radius : 
        if selection != 2: # ENTER SELECTION 2
            counter = 1
        selection = 2
        # print("selection = 2")
    elif fingers == [0, 1, 0, 0, 0] and distance(index_finger_tip, btn_list[3]) <= btn_list[3].radius : 
        if selection != 3: # ENTER SELECTION 3
            counter = 1
        selection = 3
        # print("selection = 3")
    else: # QUIT SELECTON
        # selection = -1 ##comment out in order to show button number
        counter = 0
        # print("quit selection")
        
    if counter > 0: 
        counter += 1
        print(counter, selection)
        cv2.ellipse(img, (btn_list[selection].x, btn_list[selection].y), (btn_list[selection].radius, btn_list[selection].radius), 0, 0, counter * counterspeed, (0, 255, 0), 10)
        if counter * counterspeed >= 360:
            select_mode = selection
            print("enter mode " + str(selection))
            counter = 0
            selection = -1
    return select_mode


def generate_points(clay):
    coords = []
    for i in range(0,60):
        theta = math.radians(6 * i)
        x = int(clay.x + math.sin(theta) * clay.radius)
        y = int(clay.y + math.cos(theta) * clay.radius)
        coords.append([x, y])
    return coords

def candle(img, data, fingers):
    if fingers == [1, 0, 0, 0, 0]:
        thumb = FingerTip(int(data[12]), int(data[13]))
        cv2.circle(img, (thumb.x, thumb.y), 10, orange, -1)
   
def in_circle(a, b, radius):
    """ return true if the pixel is inside the circle boundary """
    res = (a.x - b.x) ** 2 + (a.y - b.y) ** 2 - radius ** 2
    return True  if (res <=0) else False
    

def spotlight(img, data, fingers):
    h, w, _ = img.shape
    radius = 50
    
    if fingers == [1, 0, 0, 0, 0]:
        red_img = cv2.applyColorMap(img, cv2.COLORMAP_HOT)
        thumb = FingerTip(int(data[12]), int(data[13]))
        for j in range(0, h):
            for i in range(0, w):
                pixel = FingerTip(i, j)
                if in_circle(pixel, thumb, radius):
                    intensity = 1 - distance(pixel, thumb) * 0.02
                    # img[j][i] = (img[j][i][2] * 0.299 + img[j][i][1] * 0.587 + img[j][i][0] * 0.114)  # grayscale RGB = 299, 587, 114   
                    img[j][i] = red_img[j][i]
    return img

def twoFingerMode(lmList, img):
    indexFinger = FingerTip(lmList[8][0], lmList[8][1])
    middleFinger= FingerTip(lmList[12][0], lmList[12][1])
    length, _ = detector.findDistance((indexFinger.x, indexFinger.y), (middleFinger.x, middleFinger.y))
    if length < 25:
        if middleFinger.x >= WIDTH:
            middleFinger.x = WIDTH - 1
        if middleFinger.y >= HEIGHT:
            middleFinger.y = HEIGHT - 1

        click_pos = (middleFinger.y, middleFinger.x)
        cv2.circle(img, (middleFinger.x, middleFinger.y), 10, (255,0,0), cv2.FILLED)
        return click_pos

def showButtonNumber(Btn, number, img):
    cv2.putText(img, number, (Btn.x -10, Btn.y + 10), cv2.FONT_HERSHEY_PLAIN, 2, (50, 50, 50), 3)

def zeroMode(lmList, img):
    indexFinger = FingerTip(lmList[8][0], lmList[8][1])
    middleFinger = FingerTip(lmList[12][0], lmList[12][1])
    length, _ = detector.findDistance((indexFinger.x, indexFinger.y), (middleFinger.x, middleFinger.y))
    global zeroModePress
    global zeroModeDragPoint
    zeroModeDragPoint = -1

    if length < 20:
        if zeroModePress == False:
            zeroModePress = True
            if middleFinger.x >= WIDTH:
                middleFinger.x = WIDTH - 1
            if middleFinger.y >= HEIGHT:
                middleFinger.y = HEIGHT - 1
            clay_new = Clay(middleFinger.x, middleFinger.y, pink)
            clays.append(clay_new)
    elif zeroModePress == True:
        zeroModePress = False
    else :
        cv2.circle(img, (middleFinger.x, middleFinger.y), 10, pink, cv2.FILLED)

    clayID = 0
    for clay in clays:
        for i in range(0, 60, 10):
            point_center = clay.coords[i]
            length, _ = detector.findDistance(point_center, (indexFinger.x, indexFinger.y))
            if length < 25:
                global  zerModeDragPoint
                zerModeDragPoint = [clayID, i]
                #cv2.circle(img, point_center, 5, (255, 0, 0), cv2.FILLED)
        clayID += 1
if __name__ == '__main__':
    cap = cv2.VideoCapture(0) # device number = 0
    cap.set(3, WIDTH) # width 
    cap.set(4, HEIGHT) # height
    
    detector = HandDetector(maxHands=2, detectionCon=0.8) # hand detect
    selection = -1

    while True:
        if keyboard.is_pressed("q"):
            print("q is pressed")
            # Key was pressed
            break
        get_frame(cap)
    cap.release()
    cv2.destroyAllWindows()