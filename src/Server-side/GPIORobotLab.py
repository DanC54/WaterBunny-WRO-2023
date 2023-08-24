import RPi.GPIO as GPIO
import time
import RobotAPI as rapi
import threading
from gpiozero import Motor

GPIO_PWM_SERVO = 18
GPIO_PWM_MOTOR = 12

GPIO_PIN_FORWARD = 22
GPIO_PIN_BACKWARD = 23

GPIO_PIN_LEFT = 26
GPIO_PIN_RIGHT = 16

WORK_TIME = 10
DUTY_CYCLE = 50
FREQUENCY = 100


def arduino_map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

class MotorOPT:
    def __init__(self, pwm_pin: int, pin_FORWARD: int, pin_BACKWARD: int, frequency: int = 100, enable_timer = False, delay: int = 0.1) -> None:

        self.pin_FORWARD = pin_FORWARD
        self.pin_BACKWARD = pin_BACKWARD
        self.started = False
        self.timer_enabled = enable_timer
        self.timer = 0
        self.delay = delay

    def start(self):

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin_FORWARD, GPIO.OUT)
        GPIO.setup(self.pin_BACKWARD, GPIO.OUT)

        self.motor = Motor(self.pin_FORWARD, self.pin_BACKWARD)

        self.started = True

    def write(self, force: int, clockwise = True):
        if force<=0:
            force=0
        if force>=255:
            force=255
        assert self.started, "Start servo before using this method."
        if not self.timer_enabled or time.time() > self.timer:
            if clockwise:
                self.motor.backward(force / 255)
            else:
                self.motor.forward(force / 255)

            self.timer = time.time() + self.delay

    def stop(self):
        assert self.started, "Start servo before using this method."
        # self.pwm.stop()
        self.write(0)
        self.started = False

    def cleanup(self):
        GPIO.cleanup()

class Servo:

    angle = 0

    def __init__(self, servo_pwm_pin: int, servo_left_pin = GPIO_PIN_LEFT, servo_right_pin = GPIO_PIN_RIGHT, frequency: int = 100, enable_timer = False, delay: int = 0.1) -> None:
        self.pin_LEFT = servo_left_pin
        self.pin_RIGHT = servo_right_pin
        self.angle = 0
        self.started = False
        self.timer_enabled = enable_timer
        self.timer = 0
        self.delay = delay
        self.wait = False

    def start(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin_LEFT, GPIO.OUT)
        GPIO.setup(self.pin_RIGHT, GPIO.OUT)

        self.started = True

        self.motor = Motor(self.pin_LEFT, self.pin_RIGHT)

    def write(self):

        while(True):

            force: int = 0

            leftFlag: bool = False

            if self.angle >= 60:
                self.angle=60

            if self.angle <= -60:
                self.angle = -60

            if self.angle <= 0:
                self.angle = -self.angle
                leftFlag = True            

            force = self.angle * 4.25

            assert self.started, "Start servo before using this method."

            if not self.timer_enabled or time.time() > self.timer:
                if leftFlag:
                    self.motor.backward(force / 255)
                    if self.wait == True:
                        time.sleep(0.7)
                    else:
                        time.sleep(0.2)
                    self.motor.stop()
                    self.wait = False
                else:
                    self.motor.forward(force / 255)
                    if self.wait == True:
                        time.sleep(0.7)
                    else:
                        time.sleep(0.2)
                    time.sleep(0.2)
                    self.motor.stop()
                    self.wait = False
                # arduino_map(force, 0, 100, 0, 255)
        

    def stop(self):
        assert self.started, "Start servo before using this method."
        # self.pwm.stop()
        self.started = False

    def cleanup(self):
        GPIO.cleanup()


class GPIORobotApi(rapi.RobotAPI):
    def __init__(self, motor_pwm_pin = GPIO_PWM_MOTOR, motor_forward_pin = GPIO_PIN_FORWARD, motor_backward_pin = GPIO_PIN_BACKWARD, servo_pmw_pin = GPIO_PWM_SERVO, servo_left_pin = GPIO_PIN_LEFT, servo_right_pin = GPIO_PIN_RIGHT, flag_video=True, flag_keyboard=False, flag_pyboard=False, udp_stream=False, udp_turbo_stream=False, udp_event=False):
        super().__init__(flag_video, flag_keyboard, False, flag_pyboard, udp_stream, udp_turbo_stream, udp_event)
        self._servo = Servo(servo_pmw_pin, servo_left_pin, servo_right_pin)
        self._servo.start()

        self._motor = MotorOPT(motor_pwm_pin, motor_forward_pin, motor_backward_pin)
        self._motor.start()
        
        motorThread = threading.Thread(target = self._servo.write)
        motorThread.daemon = True
        motorThread.start()

    def move(self, force: int, clockwise = True):
        self._motor.write(force, clockwise)


if __name__ == "__main__":
    
    robot = GPIORobotApi()

    while(True):
        robot._servo.angle = 60
        time.sleep(1)
        robot._servo.angle = -60
        time.sleep(3)
