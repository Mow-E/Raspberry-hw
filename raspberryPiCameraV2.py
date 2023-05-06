from picamera import PiCamera
import time

class RasberryPiCameraV2:
    def __init__(self):
        self.camera = PiCamera()
    
    # Takes a picture and then saves it into the given path. 
    def takePicture(self):
        self.camera.capture("/home/admin/Documents/Embedded/RaspberryPiPhotos/collisionPicture.jpg")
    def startRecording(self):
        # For future implementations
        pass
    def stopRecording(self):
        # For future implementations
        pass

""" raspberryCamera = RasberryPiCameraV2()
raspberryCamera.takePicture() """