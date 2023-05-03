# Raspberry-hw
_Simultaneous Localization and Mapping (SLAM) Navigation using RP LIDAR A1 on RPi_

SLAM (Simultaneous Localization And Mapping) algorithms use **LiDAR and IMU data to simultaneously locate the robot in real-time and generate a coherent map of surrounding landmarks such as buildings, trees, rocks, and other world features, at the same time.**

Though a classic chicken and egg problem, it has been approximately solved using methods like **Particle Filter, Extended Kalman Filter (EKF), Covariance intersection, and GraphSLAM**. SLAM enables accurate mapping where GPS localization is unavailable, such as indoor spaces.

## How to use this repo?

```
git clone https://github.com/simondlevy/BreezySLAM.git
cd to BreezySLAM/python
sudo python3 setup.py install
```

```
git clone https://github.com/simondlevy/PyRoboViz.git
change to PyRoboViz base directory
sudo python3 setup.py install
```
Requirement

Only support python 3.6 version