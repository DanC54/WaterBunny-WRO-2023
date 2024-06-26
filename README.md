Engineering materials
====

This repository contains engineering materials of a self-driven vehicle's model participating in the WRO Future Engineers competition in the season 2023. Team "WaterBunny".

## Content

* `t-photos` contains 2 photos of the team (an official one and one funny photo with all team members).
* `v-photos` contains 6 photos of the vehicle (from every side, from top and bottom).
* `video` contains the video.md file with the link to a video where driving demonstration exists.
* `schemes` contains one or several schematic diagrams in form of JPEG, PNG or PDF of the electromechanical components illustrating all the elements (electronic components and motors) used in the vehicle and how they connect to each other.
* `src` contains code of control software for all components which were programmed to participate in the competition.

## Introduction

This repository consists of 3 main parts: `hardware`, `software` and `module description`. 

| Part          | Description   |
| ------------- |-------------: |
| [Hardware](#Hardware)      | Detailed explanation of all the physical parts of the robot, including sensors, cameras, motors |
| [Software](#Software)      | Detailed explanation of all the steps to reproduce our solution, including library requirements, operational systems, IDEs, etc. |
| [Module description](#Module-description) | Descriptions of python scripts with their purposes and algorithms  |


## Hardware

### Chassis

A simple RC toy car was used as a base for our robot. We have since replaced both motors, implemented a different power method (using the batteries that were not wired into the car), replaced all wheels, and rewired and soldered every pin connection. 

### Power management

- We have used 2 rechargeble 3.2V lithium-ion batteries (3000 Mah) to power our motors. The voltage that we chose was sufficient enough to drive our robot, yet not big enough to burn down the L298 Motor Driver. 
- In order to power up the Rapsberry Pi, we have decided to use a 5000 Mah power-bank, due to its size and weight. Due to being a little over 120g, it did not pose too much of a tension on our motors.

### L298n Motor Driver
  
In order to have complete control of the DC motor, we have to control its direction and rotation. This can be achieved by combining these two methods:

- PWM - to control the speed
- H-Bridge - To control the direction of rotation.

The speed of the DC motor can be controlled by changing the input voltage. A common approach to doing this is to use PWM (Pulse Width Modulation). The direction of rotation of the DC motor can be controlled by changing the polarity of the input voltage.
![l298n](https://github.com/DanC54/WaterBunny-WRO-2023/assets/59985928/06a660c3-8ba5-42b6-90da-4edc7f7138c7)




### DC Motor
The motor works on the principle of Lorentz force, which states: “Any conductor in which an electric current flows and is located in an external magnetic field is acted upon by a force, and the direction of the force is perpendicular to both the direction of the magnetic field and the direction of the electric current.”. DC motors are necessary in our solution in order to turn the axel of wheels to move the robot forward or backward. The steering is also controlled by the DC motor, as it would allow for the faster rotation speed compared to the servo motor.
![DCmotor](https://github.com/DanC54/WaterBunny-WRO-2023/assets/59985928/5e496dd9-6107-49da-b64d-b49eff888e32)


### Raspberry PI Camera v2.1

The camera works on capturing images continuously and the images consist of pixels - each pixel carrying only one color. The images taken by the camera are sent to the Raspberry PI to be analyzed based on the computer vision library `opencv`, so that the Raspberry will recognize the pixels which carry the color in our selected color range. It will then separate it and make a masking for it to be used in the rest of the code.
![Pi-Camera-V2-1-800x800](https://github.com/DanC54/WaterBunny-WRO-2023/assets/59985928/4f02dae5-e8df-4c94-9a48-c2f8a0f62de2)



### Planning

In order for us to avoid making any mistakes in the future, it was essential for us to know the algorithm behind the image scan. So that's why we've decided to create a flowchart to represent *barebone* algorithm that Raspberry PI will execute 
- ![262763593-b2cc1d71-7226-43da-bd43-413cf00bf784](https://github.com/DanC54/WaterBunny-WRO-2023/assets/59985928/d5f806b6-1695-4083-a3d0-c68c3f0753e7)





## Software

### On Raspberry PI (Server)

- Our robot uses Raspian OS 32 bits, officially supplied operating system by Raspberry Pi Foundation. To install the operating system, you must have a microSD. First install the [Raspberry Pi Imager](https://www.raspberrypi.com/software/) and then choose the `Raspbian OS 32 bits (Recommended)` option from the list (NOTE: All the data on the microSD will be formatted and deleted. Don't forget to backup all important files)

- After the Raspian is installed, we must enable *SSH*, *VNC* and *Legacy Camera* support using the `sudo raspi-config` command from the terminal. Go to Interface Options -> Enable Legacy Camera support/SSH/VNC and enable them one by one. Apply the changes and reboot.
- ![What-is-Raspi-Config-Tool](https://github.com/DanC54/WaterBunny-WRO-2023/assets/59985928/bc73df2f-fb2d-4272-8513-06d703fd466c)



- In order to connect to Raspberry Pi via SSH, we must first know its IPv4 address. Make sure that the Rapsberry Pi and your PC are connected to the same network, and then type `hostname -I` command into the terminal. Remember this IP address. Next, open the terminal on your PC and type `ssh [username]@[ipv4address]`. It will ask for the final confirmation, type 'yes'.

- Install all necessary libraries and dependancies by first upgrading pip (`pip3 install --upgrade pip`) and then running this command:

```
sudo apt-get update && sudo apt-get upgrade
pip install opencv-python       
pip install -U vidgear[core]
```

### On PC (Client)

- Install the libraries (On Windows):
  
  ```
  py -m pip install pip --upgrade
  pip install opencv-python
  pip install -U vidgear[core]
  pip install dxcam
  ```     

  Install Visual Studio Code. Then install the `Remote - SSH` extension.

- ![262748366-f659d4cc-ee8c-46ec-910b-5b5135142366](https://github.com/DanC54/WaterBunny-WRO-2023/assets/59985928/1053ac6d-0fb5-484d-85b2-7972f59d80ba)

  After that choose the `Connect to Host` option...
- ![262749011-9aea72c2-2ae2-4f8e-8e27-8c01cf7388fe](https://github.com/DanC54/WaterBunny-WRO-2023/assets/59985928/aa1309a0-954d-42c8-9cd7-54844ce5a0b1)

  ...and enter the `ssh [username]@[Raspberry Pi's IPv4 address]` into the pop-up menu. 

- ![262749602-7b30b04a-409b-4310-9647-297294f88405](https://github.com/DanC54/WaterBunny-WRO-2023/assets/59985928/d8aab634-0eeb-46d1-aaef-52b00ee1c63a)



- Make sure that the `TCP port 5454` is forwarded. You probably don't have to worry about it, as it almost always is. In case it isn't forwarded, check [this guide](https://www.noip.com/support/knowledgebase/general-port-forwarding-guide).


## Module description

| Part          | Description   |  Server/Client     |
| ------------- |-------------: |:-----------:  |
| `GPIORobot.py`    |  Main library used for accessing Raspberry Camera and sending frames to client (PC) via `Netgear` framework. |  Server-side   |
| `RobotApiLab.py`  |  A file containing class object of our robot. It is used for controlling servo and DC motors.   |   Server-side
| `Qualify.py`      | Code for riding 3 laps around the game mat *wihout* any obstacles. |   Server-side  |
| `Final.py`     | Code for riding 3 laps around the game mat *with* green and red obstacles.  |  Server-side   |
| `Hawkeye.py`    |  A python file used to receive processed images from Raspberry PI to Client          |    Client-side   |



### Server-side

- `GPIORobot.py`: Contains `__work_f()` and `__send_frame()` functions that run on separate threads when `GPIORobot()` class is initialized. Initializes `Netgear` framework and sends frame via it.
- `RobotAPILab.py`: Runs `Servo.write()` function as a separate thread in order to avoid using `time.sleep()` function, allowing us to avoid overheating the L298 motor driver or DC motors.
- `Qualify.py`: Contains `black_line_left()` and `black_line_right()` functions to constantly search for walls and drive away from them.
- `Final.py`: Same as above, except the function `detect_box()` was added to determine the steering angle when the camera sees red and green obstacles. 


### Client-side

- `Hawkeye.py`: Connects to the `Netgear` framework in a `receive=True` mode. Replace the `address="192.168.x.xxx"` line with your *Client's* IPv4 address (You can get this by typing `ipconfig` into Windows terminal).

You will have to modify the following code:

```
client = NetGear (
    address="192.168.x.xxx",
    port="5454",
    protocol="tcp",
    pattern=1,
    receive_mode=True,
    logging=True,
    **options
)
```

