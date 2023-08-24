__author__ = 'Yuri Glamazdin <yglamazdin@gmail.com>'
__version__ = '1.6'

# install turbo
# sudo apt-get install libturbojpeg-dev
import time
import cv2
import threading
import atexit
from vidgear.gears import PiGear
from vidgear.gears import NetGear


# for TURBO
def cv2_decode_image_buffer(img_buffer):
    img_array = np.frombuffer(img_buffer, dtype=np.dtype('uint8'))
    # Decode a colored image
    return cv2.imdecode(img_array, flags=cv2.IMREAD_UNCHANGED)


def cv2_encode_image(cv2_img, jpeg_quality):
    encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality]
    result, buf = cv2.imencode('.jpg', cv2_img, encode_params)
    return buf.tobytes()


def turbo_decode_image_buffer(img_buffer, jpeg):
    return jpeg.decode(img_buffer)


def turbo_encode_image(cv2_img, jpeg, jpeg_quality):
    return jpeg.encode(cv2_img, quality=jpeg_quality)


from ctypes import *
from ctypes.util import find_library
import numpy as np


class RobotAPI:
    port = None
    server_flag = False
    last_key = -1
    last_frame = np.ones((480, 640, 3), dtype=np.uint8)
    quality = 50
    manual_regim = 0
    manual_video = 1
    manual_speed = 150
    manual_angle = 0
    frame = np.ones((480, 640, 3), dtype=np.uint8)

    small_frame = 0
    motor_left = 0
    motor_rigth = 0
    flag_serial = False
    flag_pyboard = False
    __time_old_frame = time.time()
    time_frame = time.time() + 1000
    __cap = []
    __num_active_cam = 0
    
    stop_frames = False
    
    quality = 20
    options = {"flag": 0, "copy": False, "track": False}

    server = NetGear (
        address="192.168.137.1",
        port="5454",
        protocol="tcp",
        pattern=0,
        **options
    )


    def __init__(self, flag_video=True, flag_keyboard=True, flag_serial=True, flag_pyboard=False, udp_stream=True,
                 udp_turbo_stream=True, udp_event=True):
        
        self.flag_serial = flag_serial
        self.flag_pyboard = flag_pyboard

        atexit.register(self.cleanup)
        atexit.register(self.cleanup)
        
        self.flag_video = flag_video
        if self.flag_video == True:
            self.init_cam(0)
            
            self.server_flag = True
            self.my_thread_video = threading.Thread(target=self.__send_frame)
            self.my_thread_video.daemon = True
            self.my_thread_video.start()

        self.my_thread_f = threading.Thread(target=self.__work_f)
        self.my_thread_f.daemon = True
        self.my_thread_f.start()


    def __work_f(self):
        self.stop_frames = False

        self.alpha = 1.5 # Contrast control
        self.beta = 0 # Brightness control

        while True:

            if self.stop_frames == False and self.flag_video:
                if len(self.__cap) > 0:
                    if self.__cap[self.__num_active_cam] is not None:
                        ret, frame = self.__cap[self.__num_active_cam].read()

                        if ret is not None:

                            frame = cv2.rotate(frame, cv2.ROTATE_180)

                            #frame = cv2.convertScaleAbs(frame, alpha=self.alpha, beta=self.beta)

                            self.frame = frame
                            self.time_frame = time.time()

                            # time.sleep(0.05)
                        else:

                            self.stop_frames = True
                            self.init_cam(self.__num_active_cam)

                    else:
                        time.sleep(0.001)
                else:
                    time.sleep(0.001)

            else:
                time.sleep(0.001)


    def init_cam(self, num=0):

        while len(self.__cap) <= num:
            self.__cap.append(None)
        if self.__cap[num] is None:
            self.__cap[num] = cv2.VideoCapture(num)

        self.__num_active_cam = num

        res = self.__cap[num].isOpened()

        if res == False:
            # self.wait(100)
            # print("release cam")
            self.__cap[num].release()
            self.__cap[num] = cv2.VideoCapture(num)
            # self.__cap[num] = None
        res = self.__cap[num].isOpened()
        if res:
            self.stop_frames = False
        return res


    def end_work(self):
        
        for i in self.__cap:
            if i is not None:
                i.release()
                #self.server.close()

        if self.flag_serial:
            self.color_off()
            self.serv(0)
        self.stop_frames = True
        self.wait(300)
        self.frame = np.array([[10, 10], [10, 10]], dtype=np.uint8)
        self.wait(1000)
        print("|STOPED API")


    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_work()

    def cleanup(self):
        self.end_work()


    def set_camera(self, fps=60, width=640, height=480, num=0):
        
        answer = self.init_cam(num)
        self.stop_frames = True
        self.wait(800)

        if answer and self.__cap[num] is not None:
            self.__cap[num].set(cv2.CAP_PROP_FPS, fps)
            self.__cap[num].set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.__cap[num].set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            self.wait(600)

        self.stop_frames = False
        return answer


    def set_camera_high_res(self):
        self.set_camera(30, 1024, 720)

    def set_camera_low_res(self):
        self.set_camera(60, 320, 240)
    
    def num_activ_camera(self):
        return self.__num_active_cam

    def get_frame(self, wait_new_frame=False):
        if wait_new_frame:
            timer_max = time.time()
            while self.time_frame <= self.__time_old_frame:
                if time.time() - timer_max > 0.1:
                    break
                time.sleep(0.001)
            self.__time_old_frame = self.time_frame
        return self.frame

    def __send_frame(self):
        time1 = time.time()
        time2 = time.time()
        md = 0
        frame = 0

        while True:
            if self.last_frame is not None:
                if self.server_flag == True:
                    message = ""

                    if message == "":
                        try:

                            if time1 < self.time_frame:
                                # print("make encode")
                                # encode_param = [int(cv2.IMWRITE_JPEG_LUMA_QUALITY), self.quality]
                                self.encode_param = [int(cv2.IMWRITE_JPEG_LUMA_QUALITY), self.quality]
                                frame = self.last_frame
                                time1 = time.time()

                                md = dict(
                                    # arrayname="jpg",
                                    dtype=str(frame.dtype),
                                    shape=frame.shape,
                                )
                            
                            self.server.send(frame)


                        except:
                            pass
                    else:
                        time.sleep(0.001)
                else:
                    time.sleep(0.001)
            else:
                time.sleep(0.001)

        
    def set_frame(self, frame, quality=30):
        self.quality = quality
        self.last_frame = frame

    def wait(self, t):
        time.sleep(t / 1000)

    def text_to_frame(self, frame, text, x, y, font_color=(255, 255, 255), font_size=2):
        cv2.putText(frame, str(text), (x, y), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, font_color, font_size)
        return frame

    