Control software
====

Code that is required to reproduce the steps:
- Clone the repo by using the command `git clone https://github.com/DanC54/WaterBunny-WRO-2023.git`. Make sure you have Git installed.
- Open folder in the terminal - `cd WaterBunny-WRO-2023`
- Run `pip install -r requirements.txt` command in both "Client-side" (`cd Client-side`) folder on your PC and "Server-side" (`cd Server-side`) on your Raspberry PI.

## Server-side

Code that must be executed on Raspberry PI:

- `GPIORobot.py`: Contains `__work_f()` and `__send_frame()` functions that run on separate threads when `GPIORobot()` class is initialized. Initializes `Netgear` framework and sends frame via it.
- `RobotAPILab.py`: Runs `Servo.write()` function as a separate thread in order to avoid using `time.sleep()` function, allowing us to avoid overheating the L298 motor driver or DC motors.
- `Qualify.py`: Contains `black_line_left()` and `black_line_right()` functions to constantly search for walls and drive away from them.
- `Final.py`: Same as above, except the function `detect_box()` was added to determine the steering angle when the camera sees red and green obstacles.

## Client-side

Code that must be executed on the PC:A

- `Hawkeye.py`: Connects to the Netgear framework in a `receive=True` mode. Replace the `address="192.168.x.xxx"` line with your Client's IPv4 address (You can get this by typing ipconfig into Windows terminal).
