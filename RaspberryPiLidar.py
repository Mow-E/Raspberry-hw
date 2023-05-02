import numpy as np
import matplotlib.pyplot as plt
from rplidar import RPLidar
from sklearn.linear_model import RANSACRegressor
import math

class LidarSegmentation:
    def __init__(self, port_name='/dev/ttyUSB0', num_iterations=1000, clear_points_every=10):
        self.port_name = port_name
        self.num_iterations = num_iterations
        self.clear_points_every = clear_points_every
        self.lidar_points = []
        self.fig, self.ax = plt.subplots()
        self.ransac = RANSACRegressor()
    
    def run(self):
        # Connect to RPLidar
        lidar = RPLidar(self.port_name)
        # Start lidar data acquisition
        lidar.start_motor()
        # Print lidar health
        print(lidar.get_health())
        # Run the lidar segmentation loop
        for i, scan in enumerate(lidar.iter_scans()):
            for point in scan:
                distance = point[2]
                angle = np.radians(point[1])
                x = distance*math.cos(angle) #Get X
                y = distance*math.sin(angle) #Get Y
                self.lidar_points.append([x, y])  # Append x, y coordinates of lidar points
            if i % self.clear_points_every == 0 and i > 0:
                self.lidar_points = []
            if len(self.lidar_points) > 20:  # Wait for a sufficient number of points
                lidar_points_np = np.array(self.lidar_points)  # Convert to numpy array
                self.ransac.fit(lidar_points_np[:, 0].reshape(-1, 1), lidar_points_np[:, 1])  # Fit RANSAC model
                # Extract line parameters from RANSAC model
                inliers = self.ransac.inlier_mask_
                line_coeff = self.ransac.estimator_.coef_[0]
                line_intercept = self.ransac.estimator_.intercept_
                # Extract inlier points for the detected line
                inlier_points = lidar_points_np[inliers]
                # Clear previous plot
                self.ax.clear()
                # Plot lidar points
                self.ax.scatter(lidar_points_np[:, 0], lidar_points_np[:, 1], color='blue', s=2)
                # Plot inlier points
                self.ax.scatter(inlier_points[:, 0], inlier_points[:, 1], color='green', s=10)
                # Plot detected line
                x_range = np.array([lidar_points_np[:, 0].min(), lidar_points_np[:, 0].max()])
                y_range = line_coeff * x_range + line_intercept
                self.ax.plot(x_range, y_range, color='red', linewidth=2)
                # Set axis labels and title
                self.ax.set_xlabel('X')
                self.ax.set_ylabel('Y')
                self.ax.set_title('Line Segmentation from RPLidar Points')
                # Update the plot
                plt.draw()
                plt.pause(0.001)
            # if i >= self.num_iterations:
            #     break
        # Close RPLidar connection
        lidar.stop_motor()
        lidar.disconnect()
        # Close the matplotlib figure
        plt.close(self.fig)

if __name__ == '__main__':
    lidar_segmentation = LidarSegmentation()
    lidar_segmentation.run()