#!/usr/bin/env python3

'''
rpslam.py : BreezySLAM Python with SLAMTECH RP A1 Lidar
                 
Copyright (C) 2018 Simon D. Levy

This code is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as 
published by the Free Software Foundation, either version 3 of the 
License, or (at your option) any later version.

This code is distributed in the hope that it will be useful,     
but WITHOUT ANY WARRANTY without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License 
along with this code.  If not, see <http://www.gnu.org/licenses/>.
'''

from rplidar import *
from breezyslam.algorithms import RMHC_SLAM
from breezyslam.sensors import RPLidarA1 as LaserModel
from rplidar import RPLidar as Lidar
from roboviz import MapVisualizer

MAP_SIZE_PIXELS         = 500
MAP_SIZE_METERS         = 12
LIDAR_DEVICE            = '/dev/ttyUSB0'

MIN_SAMPLES   = 150 # 150 points at a time

class Positioning:
    def __init__(self):
        #Connect to Lidar unit
        self.lidar = Lidar(LIDAR_DEVICE)
        
        # Create an RMHC SLAM object with a laser model and optional robot model
        self.slam = RMHC_SLAM(LaserModel(), MAP_SIZE_PIXELS, MAP_SIZE_METERS)

        # Set up a SLAM display
        self.viz = MapVisualizer(MAP_SIZE_PIXELS, MAP_SIZE_METERS, 'SLAM')

        # Initialize an empty trajectory
        self.trajectory = []

        # Initialize empty map
        self.mapbytes = bytearray(MAP_SIZE_PIXELS * MAP_SIZE_PIXELS)

        # Create an iterator to collect scan data from the RPLidar
        self.iterator = self.lidar.iter_scans(scan_type='normal', max_buf_meas= 4000)

        # We will use these to store previous scan in case current scan is inadequate
        self.previous_distances = None
        self.previous_angles    = None

        # First scan is crap, so ignore it
        next(self.iterator)
    
    def constructmap(self):
        try:
            while True:
                
                # Extract (quality, angle, distance) triples from current scan
                self.items = [item for item in next(self.iterator)]

                # Extract distances and angles from triples
                self.distances = [item[2] for item in self.items]
                self.angles    = [item[1] for item in self.items]

                # Update SLAM with current Lidar scan and scan angles if adequate
                if len(self.distances) > MIN_SAMPLES:
                    self.slam.update(self.distances, scan_angles_degrees=self.angles)
                    self.previous_distances = self.distances.copy()
                    self.previous_angles    = self.angles.copy()

                # If not adequate, use previous
                elif self.previous_distances is not None:
                    self.slam.update(self.previous_distances, scan_angles_degrees=self.previous_angles)

                # Get current robot position
                x, y, theta = self.slam.getpos()

                # Get current map bytes as grayscale
                self.slam.getmap(self.mapbytes)

                # Display map and robot pose, exiting gracefully if user closes it
                if not self.viz.display(x/1000., y/1000., theta, self.mapbytes):
                    exit(0)

        except RPLidarException:
            #clear input to clean the buffer:
            self.lidar.clean_input() 
            # Shut down the lidar connection
            self.lidar.stop()
            self.lidar.stop_motor()
            self.lidar.disconnect()

if __name__ == "__main__":
    mower_position = Positioning()
    mower_position.constructmap()