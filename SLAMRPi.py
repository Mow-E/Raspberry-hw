"""

This file as been modified extensively to implement SLAM in RPLidar.
It can run well on Raspberry Pi 3B or 4

Many concepts are taken from rpslam.py : BreezySLAM in Python with SLAMTECH RP A1 Lidar
https://github.com/simondlevy/BreezySLAM

Consume LIDAR measurement file and create an image for display.

Adafruit invests time and resources providing this open source code.
Please support Adafruit and open source hardware by purchasing
products from Adafruit!

Written by Dave Astels for Adafruit Industries
Copyright (c) 2019 Adafruit Industries
Licensed under the MIT license.

All text above must be included in any redistribution.
"""

""" import os
import time
import json """
""" 

from math import cos, sin, pi, floor
# import pygame
import rplidar
from rplidar import RPLidar, RPLidarException
import numpy as np

import matplotlib.pyplot as plt
from threading import Thread """
import time
from math import cos, sin, pi, floor
#import rplidar
from rplidar import RPLidar, RPLidarException
import numpy as np
import matplotlib.pyplot as plt
from threading import Thread
#from breezyslam.algorithms import RMHC_SLAM
from breezyslam.sensors import RPLidarA1 as LaserModel
from roboviz import MapVisualizer


from breezyslam.algorithms import RMHC_SLAM
from breezyslam.sensors import RPLidarA1 as LaserModel
# from rplidar import RPLidar as Lidar
# from adafruit_rplidar import RPLidar as Lidar
from roboviz import MapVisualizer






class SLAMRPi:
    # Setup the RPLidar
    def __init__(self):
        # Screen width & height
        W = 640
        H = 480

        self.MAP_SIZE_PIXELS         = 250
        self.MAP_SIZE_METERS         = 5
        self.MIN_SAMPLES   = 150
        
        self.SCAN_BYTE = b'\x20'
        self.SCAN_TYPE = 129
        
        self.PORT_NAME = '/dev/ttyUSB0'
        self.lidar = RPLidar(self.PORT_NAME)
        
        # Create an RMHC SLAM object with a laser model and optional robot model
        self.slam = RMHC_SLAM(LaserModel(), self.MAP_SIZE_PIXELS, self.MAP_SIZE_METERS)
        
        # # Set up a SLAM display
        #self.viz = MapVisualizer(self.MAP_SIZE_PIXELS, self.MAP_SIZE_METERS, 'SLAM', show_trajectory=True)
        
        # Initialize an empty trajectory
        self.trajectory = []

        #Define a filename for json file
        self.filename = 'lidar_data.json'
        #Create an empty dictionary to store lidar data

        self.slamData = {'Current_position':[]}
        #Store current position
   
        self.current_position = []
        # To exit lidar scan thread gracefully
 
        self.thread = None

        # Initialize empty map
        self.mapbytes = bytearray(self.MAP_SIZE_PIXELS * self.MAP_SIZE_PIXELS)

        # used to scale data to fit on the screen
        self.max_distance = 0
        # x, y, theta = 0, 0, 0

        # Pose will be modified in our threaded code
        self.pose = [0, 0, 0]
        self.x = 0
        self.y = 0
        self.scan_data = [0]*360

    def slam_compute(self,pose, mapbytes):
        
        try:

            # We will use these to store previous scan in case current scan is inadequate
            self.previous_distances = None
            self.previous_angles = None
            self.scan_count = 0
            
            for scan in self.lidar.iter_scans():
                
                

                # To stop the thread
                #if not self.runThread:
                #   break

                self.scan_count += 1

                # Extract (quality, angle, distance) triples from current scan
                self.items = [item for item in scan]

                # Extract distances and angles from triples
                self.distances = [item[2] for item in self.items]
                self.angles = [item[1] for item in self.items]

                # Update SLAM with current Lidar scan and scan angles if adequate
                if len(self.distances) > self.MIN_SAMPLES:
                    self.slam.update(self.distances, scan_angles_degrees=self.angles)
                    self.previous_distances = self.distances.copy()
                    self.previous_angles    = self.angles.copy()

                # If not adequate, use previous
                elif self.previous_distances is not None:
                    self.slam.update(self.previous_distances, scan_angles_degrees=self.previous_angles)

                # Get new position
                self.pose[0], self.pose[1], self.pose[2] = self.slam.getpos()
                self.slam.getmap(mapbytes)
        except KeyboardInterrupt:
            self.lidar.stop()
            self.lidar.disconnect()
            raise

    def compute_position(self):
        self.thread = Thread(target= self.slam_compute, args = (self.pose, self.mapbytes))
        self.thread.start()
        print("Thread started")

    def join_thread(self):
        if self.thread:
            self.thread.join()
            #print("Thread joined")
        else:
            print("No active thread")

    def get_position(self):
        self.x =  2500 - self.pose[0]
        self.y =  2500 - self.pose[1]
        return (self.x,self.y)


