"""
The Motion Detection class.
"""

import numpy
import picamera.array
from threading import Event

THRESHOLD = 60  # Magnitude of motion vector
SENSITIVITY = 15  # Number of motion vectors  

OUTPUT_ID = "motion_detector"
class MotionDetector:
    def __init__(self, threshold = THRESHOLD, sensitivity = SENSITIVITY):
        self.threshold = threshold
        self.sensitivity = sensitivity
        self.motion_detected = Event()

    def analyse(self, motion_vectors):
        self.motion_detected.clear()
        motion_vectors = numpy.sqrt(
            numpy.square(motion_vectors['x'].astype(numpy.float)) +
            numpy.square(motion_vectors['y'].astype(numpy.float))
        ).clip(0, 255).astype(numpy.uint8)
        if (motion_vectors > THRESHOLD).sum() > SENSITIVITY:
            self.motion_detected.set()

    def calibrate(self, no_motion_seconds = 5, max_resets = 5):
        reset_count = 0
        while self.motion_detected.wait(5):
            reset_count += 1
            if reset_count > max_resets:
                return False
        return True