Control software
====

## Server-side

Code that must be executed on Raspberry PI:

- `GPIORobot.py`: Contains `__work_f()` and `__send_frame()` functions that run on separate threads when `GPIORobot()` class is initialized. Initializes `Netgear` framework and sends frame via it.
- `RobotAPILab.py`: Runs `Servo.write()` function as a separate thread in order to avoid using `time.sleep()` function, allowing us to avoid overheating the L298 motor driver or DC motors.
- `Qualify.py`: Contains `black_line_left()` and `black_line_right()` functions to constantly search for walls and drive away from them.
- `Final.py`: Same as above, except the function `detect_box()` was added to determine the steering angle when the camera sees red and green obstacles.

## Client-side

Code that must be executed on the PC:A

- `Hawkeye.py`: Connects to the Netgear framework in a `receive=True` mode. Replace the `address="192.168.x.xxx"` line with your Client's IPv4 address (You can get this by typing ipconfig into Windows terminal).
