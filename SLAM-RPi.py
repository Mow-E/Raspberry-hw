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

import os
import time
import json
from math import cos, sin, pi, floor
# import pygame
import rplidar
from rplidar import RPLidar, RPLidarException
import numpy as np
import matplotlib.pyplot as plt
from threading import Thread


from breezyslam.algorithms import RMHC_SLAM
from breezyslam.sensors import RPLidarA1 as LaserModel
# from rplidar import RPLidar as Lidar
# from adafruit_rplidar import RPLidar as Lidar
from roboviz import MapVisualizer



# Screen width & height
W = 640
H = 480


MAP_SIZE_PIXELS         = 250
MAP_SIZE_METERS         = 5
MIN_SAMPLES   = 150

SCAN_BYTE = b'\x20'
SCAN_TYPE = 129



# Setup the RPLidar
PORT_NAME = '/dev/ttyUSB0'
lidar = RPLidar(PORT_NAME)

# Create an RMHC SLAM object with a laser model and optional robot model
slam = RMHC_SLAM(LaserModel(), MAP_SIZE_PIXELS, MAP_SIZE_METERS)

# # Set up a SLAM display
viz = MapVisualizer(MAP_SIZE_PIXELS, MAP_SIZE_METERS, 'SLAM', show_trajectory=True)

# Initialize an empty trajectory
trajectory = []

#Define a filename for json file
filename = 'lidar_data.json'
#Create an empty dictionary to store lidar data
slamData = {'Current_position':[]}
#Store current position
current_position = []
# To exit lidar scan thread gracefully
runThread = True

# Initialize empty map
mapbytes = bytearray(MAP_SIZE_PIXELS * MAP_SIZE_PIXELS)

# used to scale data to fit on the screen
max_distance = 0
# x, y, theta = 0, 0, 0

# Pose will be modified in our threaded code
pose = [0, 0, 0]

scan_data = [0]*360

def _process_scan(raw):
    '''Processes input raw data and returns measurment data'''
    new_scan = bool(raw[0] & 0b1)
    inversed_new_scan = bool((raw[0] >> 1) & 0b1)
    quality = raw[0] >> 2
    if new_scan == inversed_new_scan:
        raise RPLidarException('New scan flags mismatch')
    check_bit = raw[1] & 0b1
    if check_bit != 1:
        raise RPLidarException('Check bit not equal to 1')
    angle = ((raw[1] >> 1) + (raw[2] << 7)) / 64.
    distance = (raw[3] + (raw[4] << 8)) / 4.
    return new_scan, quality, angle, distance

def iter_measures(self, scan_type='normal', max_buf_meas=3000):
        '''Iterate over measures. Note that consumer must be fast enough,
        otherwise data will be accumulated inside buffer and consumer will get
        data with increasing lag.
        Parameters
        ----------
        max_buf_meas : int or False if you want unlimited buffer
            Maximum number of bytes to be stored inside the buffer. Once
            numbe exceeds this limit buffer will be emptied out.
        Yields
        ------
        new_scan : bool
            True if measures belongs to a new scan
        quality : int
            Reflected laser pulse strength
        angle : float
            The measure heading angle in degree unit [0, 360)
        distance : float
            Measured object distance related to the sensor's rotation center.
            In millimeter unit. Set to 0 when measure is invalid.
        '''
        self.start_motor()
        if not self.scanning[0]:
            self.start(scan_type)
        while True:
            dsize = self.scanning[1]
            if max_buf_meas:
                data_in_buf = self._serial.inWaiting()
                if data_in_buf > max_buf_meas:
                    self.logger.warning(
                        'Too many bytes in the input buffer: %d/%d. '
                        'Cleaning buffer...',
                        data_in_buf, max_buf_meas)
                    self.stop()
                    self.start(self.scanning[2])

            if self.scanning[2] == 'normal':
                raw = self._read_response(dsize)
                yield _process_scan(raw)
            if self.scanning[2] == 'express':
                if self.express_trame == 32:
                    self.express_trame = 0
                    if not self.express_data:
                        self.logger.debug('reading first time bytes')
                        self.express_data = ExpressPacket.from_string(
                                            self._read_response(dsize))

                    self.express_old_data = self.express_data
                    self.logger.debug('set old_data with start_angle %f',
                                      self.express_old_data.start_angle)
                    self.express_data = ExpressPacket.from_string(
                                        self._read_response(dsize))
                    self.logger.debug('set new_data with start_angle %f',
                                      self.express_data.start_angle)

                self.express_trame += 1
                self.logger.debug('process scan of frame %d with angle : '
                                  '%f and angle new : %f', self.express_trame,
                                  self.express_old_data.start_angle,
                                  self.express_data.start_angle)
                yield _process_express_scan(self.express_old_data,
                                            self.express_data.start_angle,
                                            self.express_trame)

def iter_scans(self, scan_type='normal', max_buf_meas=3000, min_len=5):
        '''Iterate over scans. Note that consumer must be fast enough,
        otherwise data will be accumulated inside buffer and consumer will get
        data with increasing lag.
        Parameters
        ----------
        max_buf_meas : int
            Maximum number of measures to be stored inside the buffer. Once
            numbe exceeds this limit buffer will be emptied out.
        min_len : int
            Minimum number of measures in the scan for it to be yelded.
        Yields
        ------
        scan : list
            List of the measures. Each measurment is tuple with following
            format: (quality, angle, distance). For values description please
            refer to `iter_measures` method's documentation.
        '''
        scan_list = []
        iterator = self.iter_measures(scan_type, max_buf_meas)
        for new_scan, quality, angle, distance in iterator:
            if new_scan:
                if len(scan_list) > min_len:
                    yield scan_list
                scan_list = []
            if distance > 0:
                scan_list.append((quality, angle, distance))

def slam_compute(pose, mapbytes):

    try:

        # We will use these to store previous scan in case current scan is inadequate
        previous_distances = None
        previous_angles = None
        scan_count = 0

        for scan in iter_scans(lidar):

            # To stop the thread
            if not runThread:
                break

            scan_count += 1

            # Extract (quality, angle, distance) triples from current scan
            items = [item for item in scan]

            # Extract distances and angles from triples
            distances = [item[2] for item in items]
            angles = [item[1] for item in items]

            # Update SLAM with current Lidar scan and scan angles if adequate
            if len(distances) > MIN_SAMPLES:
                slam.update(distances, scan_angles_degrees=angles)
                previous_distances = distances.copy()
                previous_angles    = angles.copy()

            # If not adequate, use previous
            elif previous_distances is not None:
                slam.update(previous_distances, scan_angles_degrees=previous_angles)

            # Get new position
            pose[0], pose[1], pose[2] = slam.getpos()

            # Get current map bytes as grayscale
            slam.getmap(mapbytes)
    except KeyboardInterrupt:
        lidar.stop()
        lidar.disconnect()
        raise

def get_position():
    x = 2500 - pose[0]
    y = 2500 - pose[1]
    return (x,y)

# Launch the slam computation thread
thread = Thread(target=slam_compute,
                args=(pose, mapbytes))
thread.daemon = True
thread.start()

try:
    # Loop forever,displaying current map and pose
    while True:
        # print("x = " + str(pose[0]) + " y = " + str(pose[1]) + "theta = " + str(pose[2]))
        print("x,y:", get_position())
        if not viz.display(pose[0]/1000., pose[1]/1000., pose[2], mapbytes):
            raise KeyboardInterrupt
        
except KeyboardInterrupt:
    runThread = False
    thread.join()
    lidar.stop()
    lidar.disconnect()
    exit(0)