"""
SinglePiCamera class

Since only one instance of PiCamera can exist this
simply wraps the PiCamera object in a singleton class.
"""

from picamera import PiCamera

class SinglePiCamera:
    instance = None
    def __init__(self, **options):
        if not SinglePiCamera.instance:
            SinglePiCamera.instance = PiCamera(**options)

    def __getattr__(self, attr):
        return getattr(self.instance, attr)