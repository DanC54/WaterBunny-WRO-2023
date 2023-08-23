Engineering materials
====

This repository contains engineering materials of a self-driven vehicle's model participating in the WRO Future Engineers competition in the season 2022.

## Content

* `team-photos` contains 2 photos of the team (an official one and one funny photo with all team members).
* `robot-photos` contains 6 photos of the vehicle (from every side, from top and bottom).
* `video` contains the video.md file with the link to a video where driving demonstration exists.
* `schemes` contains one or several schematic diagrams in form of JPEG, PNG or PDF of the electromechanical components illustrating all the elements (electronic components and motors) used in the vehicle and how they connect to each other.
* `src` contains code of control software for all components which were programmed to participate in the competition.

## Introduction

This repository consists of 3 main parts: `hardware`, `software` and `module description`. 

| Part          | Description   |
| ------------- |-------------: |
| Hardware      | Detailed explanation of all the physical parts of the robot, including sensors, cameras, motors |
| Software      | Detailed explanation of all the steps to reproduce our solution, including library requirements, operational systems, IDEs, etc. |
| Module description | Descriptions of python scripts with their purposes and algorithms  |


## Hardware




## Software

### On Raspberry PI (Server)

- Our robot uses Raspian OS 32 bits, officially supplied operating system by Raspberry Pi Foundation. To install the operating system, you must have a microSD. First install the Raspberry Pi Imager and then choose the `Raspbian OS 32 bits (Recommended)` option from the list (NOTE: All the data on the microSD will be formatted and deleted. Don't forget to backup all important files)

- After the Raspian is installed, we must enable *SSH*, *VNC* and *Legacy Camera* support using the `sudo raspi-config` command from the terminal. Apply the changes and reboot.

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

- Make sure that the TCP port 5454 is forwarded. You probably don't have to worry about it, as it almost always is. In case it isn't forwarded, check this guide. 


## Module desription

- GPIORobot.py

