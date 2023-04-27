from picamera import PiCamera
import time

class RasberryPiCameraV2:
    def __init__(self):
        self.camera = PiCamera()
    def takePicture(self):
        self.camera.capture("/home/admin/Documents/Embedded/RaspberryPiPhotos/test.jpg")
    def startRecording(self):
        # For future implementations
        pass
    def stopRecording(self):
        # For future implementations
        pass

""" raspberryCamera = RasberryPiCameraV2()
raspberryCamera.takePicture() """