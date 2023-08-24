import cv2
import numpy as np
import time

# initializing constants for hsv
BLACK_UP = np.array([180, 255, 70])  # for walls
BLACK_LOW = np.array([0, 0, 0])
ORANGE_UP = np.array([30, 255, 255])  # for orange lines
ORANGE_LOW = np.array([0, 40, 80])
BLUE_UP = np.array([130, 255, 170])  # for blue lines
BLUE_LOW = np.array([100, 90, 20])
GREEN_UP = np.array([90, 255, 200])  # for green signs
GREEN_LOW = np.array([50, 100, 55])
RED_UP_1 = np.array([10, 255, 255])   # for red signs
RED_LOW_1 = np.array([0, 50, 50])
RED_UP_2 = np.array([20, 230, 240])
RED_LOW_2 = np.array([0, 70, 120])

DRAW = True  # initializing constants for drawing the borders on the image

# initializing constants for coordinates of areas in the image
X1_1_PD = 390  # for walls
X2_1_PD = 640
X1_2_PD = 0
X2_2_PD = 250
Y1_PD = 290
Y2_PD = 450

X1_LINE = 300  # for counting lines
X2_LINE = 380
Y1_LINE = 360
Y2_LINE = 470

X1_CUB = 30  # for sings detection
X2_CUB = 625
Y1_CUB = 220
Y2_CUB = 430

# initializing constants of ratio for controllers
KP = 0.013  # the proportional gain, a tuning parameter for walls
KD = 0.05  # the derivative gain, a tuning parameter for walls
K_X = 0.05  # the proportional gain, a tuning parameter for signs
K_Y = 0.04  # the derivative gain, a tuning parameter for signs


class Frames:  # clsss for areas on the picture
    def __init__(self, img, x_1, x_2, y_1, y_2, low, up):  # init gains coordinates of the area, and hsv boders
        self.x_1 = x_1  # initializing variables in class
        self.x_2 = x_2
        self.y_1 = y_1
        self.y_2 = y_2
        self.up = up
        self.low = low

        self.contours = 0
        self.frame = 0
        self.hsv = 0
        self.mask = 0
        self.frame_gaussed = 0

        self.update(img)

    def update(self, img):  # function for updating the image
        # getting the needed area on the image and outlining it
        cv2.rectangle(img, (self.x_1, self.y_1), (self.x_2, self.y_2), (150, 0, 50), 2)

        self.frame = img[self.y_1:self.y_2, self.x_1:self.x_2]
        self.frame_gaussed = cv2.GaussianBlur(self.frame, (1, 1), cv2.BORDER_DEFAULT)  # blurring the image

        self.hsv = cv2.cvtColor(self.frame_gaussed, cv2.COLOR_BGR2HSV)  # turning the image from bgr to hsv

    def find_contours(self, n=0, to_draw=True, color=(0, 0, 255), min_area=50, red_dop=0):  # function for selecting
        # the contours, it gets, the needed borders of hsv, if the borders should be drawn, color of the outlining,
        # minimum area of the contour, and if it is used for red signs
        self.mask = cv2.inRange(self.hsv, self.low[n], self.up[n])  # getting the mask
        if red_dop == 1:
            mask_1 = cv2.inRange(self.hsv, self.low[n + 1], self.up[n + 1])
            self.mask = cv2.bitwise_or(self.mask, mask_1)

        contours, hierarchy = cv2.findContours(self.mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)  # getting contours
        r_contours = []
        for i in contours:  # outlining and selecting only big enough contours
            if cv2.contourArea(i) > min_area:
                r_contours.append(i)
                if to_draw:
                    cv2.drawContours(self.frame, i, -1, color, 2)

        return r_contours  # returning contours


def pd():  # function of proportional–derivative controller for walls
    global pd_1, pd_2, KD, KP, e_old, timer_flag, time_turn, tim
    global flag_left, flag_right, u  # needed global variables for this function

    u_plus = 0  # getting the addition to pd, to compensate the angle of the camera
    if direction == 'wise':
        u_plus = -10
    if direction == 'counter wise':
        u_plus = -15

    contours = pd_1.find_contours(to_draw=DRAW, color=(255, 255, 0))  # getting the contours for 1_st area
    area_1 = map(cv2.contourArea, contours)  # getting the area of the biggest contour
    if contours:
        area_1 = max(area_1)
    else:
        area_1 = 0

    contours = pd_2.find_contours(to_draw=DRAW, color=(255, 255, 0))  # same for 2_nd area
    area_2 = map(cv2.contourArea, contours)
    if contours:
        area_2 = max(area_2)
    else:
        area_2 = 0

    e = area_2 - area_1  # counting the error and the final value of pd
    u = e * KP + ((e - e_old) // 10) * KD + 128 + u_plus
    e_old = e

    if u >= 160:  # limiting the turning of servo
        u = 160

    if area_2 != 0 and area_1 == 0:  # if there is no wall in one of ares, turning to the max to needed side
        flag_right = True  # changing the flag or turning
        if not timer_flag:  # resetting the timer of turning
            if time.time() < 0.2:  # if the turn, right after the inner sing, turn to the max
                if direction == 'wise':
                    time_turn = time.time() - 5
            else:
                time_turn = time.time()
            timer_flag = True

        if time.time() - time_turn > 0.1:
            u = 160

        else:
            u = 140

    elif area_1 != 0 and area_2 == 0:  # same as the previous
        flag_left = True
        if not timer_flag:
            if time.time() < 0.2:
                if direction == 'counter wise':
                    time_turn = time.time() - 5
            else:
                time_turn = time.time()

            timer_flag = True

        if time.time() - time_turn > 0.1:
            u = 40
        else:
            u = 80

    elif area_1 == 0 and area_2 == 0:  # if there's no wall in any area, turn to the same side as before
        if flag_right:  #####
            if time.time() - time_turn > 0.1:
                u = 160
            else:
                u = 140

        elif flag_left:     #####
            if time.time() - time_turn > 0.1:
                u = 40
            else:
                u = 80

    else:  # else resetting the flags
        flag_left = False
        flag_right = False
        timer_flag = False

    if u <= 60:  # limiting the max turning for servo
        u = 40

    if area_1 + area_2 == 0 and direction is not None:
            if direction == "wise":
                u = 40
            else:
                u = 160

    return int(u - 100)  # returning controlling influence of pd


def pd_cub(color):  # function of proportional–derivative controller for signs
    global direction, K_X, K_Y, frame, time_red, time_green, cub

    if color == 'green':  # getting the contours depending on the color
        countors = cub.find_contours(to_draw=DRAW, color=(0, 255, 0), min_area=1000)
    elif color == 'red':
        countors = cub.find_contours(1, DRAW, min_area=1000, red_dop=1)
    else:
        print('color erorr')
        return -1  # if the color is not right, return -1

    if countors:
        countors = max(countors, key=cv2.contourArea)  # if there is contours, getting the biggest of them
        x, y, w, h = cv2.boundingRect(countors)  # getting the coordinates of the contour
        x = (2 * x + w) // 2
        y = y + h

        if color == 'red':  # defining the needed coordinate, depending on the color
            time_red = time.time()
            x_tar = 0
        elif color == 'green':
            time_green = time.time()
            x_tar = cub.x_2 - cub.x_1
        else:
            print('color erorr')
            return -1

        e_x = round((x_tar - x) * K_X, 3)  # error for x coordinate
        e_y = round(y * K_Y, 3)  # error for y coordinate
        e_cub = int(abs(e_y) + abs(e_x))  # getting the error for both coordinates

        if color == 'green':
            if direction == 'wise':
                e_cub = int(e_cub * -1.5)
            else:
                e_cub = int(e_cub * -1.8)
        if color == 'red':
            if direction == 'wise':
                e_cub = int(e_cub * 1.25)
        if color == 'green':  # printing the error on the image
            frame = cv2.putText(frame, str(e_cub), (20, 60),
                                cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
        else:
            frame = cv2.putText(frame, str(e_cub), (20, 90),
                                cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)

        return e_cub  # returning the erorr

    return -1  # if there's no signs in the area, return -1


def restart():  # function for resetting all the variables
    global orange, blue, u, e_old, tim, time_orange, time_blue, stop_flag, time_turn, time_green, time_red, time_speed
    global pause_flag, flag_line_blue, flag_line_orange, direction, time_stop, flag_left, flag_right, timer_flag, speed_def

    orange = 0
    blue = 0

    timer_flag = False

    speed_def = 160

    u = 125
    e_old = 0

    tim = time.time()
    time_orange = time.time() - 5
    time_blue = time.time() - 5
    time_turn = time.time() - 5
    time_green = time.time() - 2
    time_red = time.time() - 2
    time_speed = time.time() + 200
    time_stop = time.time()

    stop_flag = False
    pause_flag = False
    flag_left = False
    flag_right = False
    flag_line_orange = False
    flag_line_blue = False

    direction = ''



orange = 0  # variables, for counting lines
blue = 0

u = 125  # variables for pd
e_old = 0
speed_def = 160

# initializing timers
tim = time.time()  # for finish
time_orange = time.time() - 5  # for counting orange lines
time_blue = time.time() - 5  # for counting blue lines
time_turn = time.time() - 5  # for turns
time_green = time.time() - 2  # for green sings
time_red = time.time() - 2  # for red signs
time_speed = time.time() + 200  # for slowing down at the start(optional)
time_stop = time.time()  # for stopping the robot

# initializing flags
timer_flag = False  # for resetting other variables only once
stop_flag = False  # for stopping the robot
pause_flag = False  # for pausing the robot
flag_left = False  # for tracking turns to the left
flag_right = False  # for tracking turns to the right
flag_line_orange = False  # for tracking orange lines
flag_line_blue = False  # for tracking blue lines
after_cub = False  # for tracking turns after sings

direction = ''  # direction variable

from GPIORobotLab import GPIORobotApi

robot = GPIORobotApi()  # initializing object needed to manage the camera
robot.set_camera(40, 640, 480)  # setting up the camera
frame = robot.get_frame(wait_new_frame=1)

# initializing objects for different areas
pd_1 = Frames(frame, X1_1_PD, X2_1_PD, Y1_PD, Y2_PD, [BLACK_LOW], [BLACK_UP])  # for the right wall
pd_2 = Frames(frame, X1_2_PD, X2_2_PD, Y1_PD, Y2_PD, [BLACK_LOW], [BLACK_UP])  # for the left wall
line = Frames(frame, X1_LINE, X2_LINE, Y1_LINE, Y2_LINE, [BLUE_LOW, ORANGE_LOW], [BLUE_UP, ORANGE_UP])  # for counting
# lines
# for detection signs
cub = Frames(frame, X1_CUB, X2_CUB, Y1_CUB, Y2_CUB, [GREEN_LOW, RED_LOW_1, RED_LOW_2], [GREEN_UP, RED_UP_1, RED_UP_2])

robot.set_frame(frame, 40)

# variables for counting fps
time_fps = time.time()
fps = 0
fps_last = 0

buttonFlag = False

def telemetry(): # функция вывода телеметрии
    robot.text_to_frame(frame, 'a_red = ' + str(u_green), 10, 20,(255,122,122))
    robot.text_to_frame(frame, 'speed = ' + str(speed), 10, 40,(0,0,255))
    robot.text_to_frame(frame, 'serv = ' + str(int(u)), 10, 60,(255,255,0))
    robot.text_to_frame(frame, 'fps = ' + str(fps_last), 505, 20)
    robot.text_to_frame(frame, 'a_red = ' + str(u_red), 480, 40,(122,122,255))

    if direction is not None:
        if direction==1:
            robot.text_to_frame(frame, 'Lin(+)=' + str(orange), 485, 60,(0,0,0))
        else:
            robot.text_to_frame(frame, "Lin(-)=" + str(blue), 470, 60,(50,50,50))


while True:  # main loop

    while True:
        if robot._button.check() == True or buttonFlag == True:
            buttonFlag = True
            break
    
    if time.time() - time_speed > 3:  # checking of the speed raising
        speed_def = 250
    # resetting controlling influence and speed
    u = -1
    speed = speed_def
    fps += 1
    frame = robot.get_frame(wait_new_frame=1)  # getting image from camera

    cub.update(frame)  # updating sign area

    u_red = pd_cub('red')  # getting controlling influence for red sings
    u_green = pd_cub('green')  # getting controlling influence for green sings
    if u_green != -1:
        u = -60 # if there is sings, counting final controlling influence
    elif u_red != -1:
        u = 60
    else:
        pd_1.update(frame)  # updating wall areas
        pd_2.update(frame)
        u = pd()  # counting controlling influence

    line.update(frame)  # updating line-counting area
    contours_blue = line.find_contours(0, DRAW, min_area=500)  # getting bue and orange areas
    contours_orange = line.find_contours(1, DRAW, min_area=500, color=(255, 255, 0))

    if contours_blue:  # if there is blue contour, checking, if the line is new, and adding it
        contours_blue = max(contours_blue, key=cv2.contourArea)
        ar = cv2.contourArea(contours_blue)
        if ar > 10:
            if not flag_line_blue and time.time() - time_blue > 1:
                if not direction:
                    direction = 'counter wise'
                blue += 1
                if blue == 1 and orange == 0:
                    time_speed = time.time()
                print('orange: ' + str(orange) + '\n blue: ' + str(blue))
                time_blue = time.time()  # resetting timer for blue lines
                tim = time.time()  # resetting timer for stopping
            flag_line_blue = True
    else:
        flag_line_blue = False

    if contours_orange:  # same as for blue line
        contours_orange = max(contours_orange, key=cv2.contourArea)
        ar = cv2.contourArea(contours_orange)
        if ar > 10:
            if not flag_line_orange and time.time() - time_orange > 1:
                if not direction:
                    direction = 'wise'
                orange += 1
                if orange == 1 and blue == 0:
                    time_speed = time.time()
                time_orange = time.time()
                print('orange: ' + str(orange) + '\n blue: ' + str(blue))
                tim = time.time()
            flag_line_orange = True
    else:
        flag_line_orange = False

    if (max(orange, blue) > 11 and time.time() - tim > 1.2) or stop_flag:  # checking if the robot must stop
        if not stop_flag:
            time_stop = time.time()
        if time.time() - time_stop < 0.3:  # braking for 0.3 seconds
            speed = -50
            #u = 127
        else:  # stopping the robot
            #u = 127
            speed = 0
        #stop_flag = True

    if pause_flag:  # checking if the robot is paused
        u = 127
        speed = 0

    if not stop_flag:  # checking if robot is not stopped/breaking
        frame = cv2.putText(frame, ' '.join([str(speed), str(u), str(fps_last)]), (20, 30),
                            cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)  # printing parameters on the image
        
        if u < 0:
            if u > -50: 
                u = -50
        elif u > 0:
            if u < 50:
                u = 50

        robot.move(speed_def)
        robot._servo.angle = -u

    if stop_flag:
        if direction == 'wise':
            robot._servo.angle = 60
            robot.move(190)
            time.sleep(1.3)
            robot.move(0)
        
        else:
            robot._servo.angle = -60
            robot.move(190)
            time.sleep(1.3)
            robot.move(0)
        
    
    if time.time() - time_fps > 1:  # counting fps
        time_fps = time.time()
        fps_last = fps
        fps = 0
    
    telemetry()

    robot.set_frame(frame, 40)  # sending changed image

    key = 100

    if key != -1:
        if key == 83:  # if s is clicked, pausing the robot
            pause_flag = True
        elif key == 71:  # if g is clicked unpausing the robot
            pause_flag = False
        elif key == 82:  # if r is clicked restarting the robot
            restart()
