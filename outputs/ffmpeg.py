import os
from subprocess import Popen, PIPE
from utils.single_picamera import SinglePiCamera

BITRATE = 2000000  # Good bitrate for high quality video

OUTPUT_ID = "ffmpeg"
class FFMPEGOutput(object):
    def __init__(self, bitrate = BITRATE):
        self.kbitrate = int(bitrate / 1000.0)
        self.converter = None

    def start_ffmpeg_converter(self):
        self.converter = Popen([
            'ffmpeg',
            '-f', 'rawvideo',
            '-pix_fmt', 'yuv420p',
            '-s', '%dx%d' % SinglePiCamera().resolution,
            '-r', str(float(SinglePiCamera().framerate)),
            '-i', '-',
            '-f', 'mpeg1video',
            '-b', '%dk' % self.kbitrate,
            '-r', str(float(SinglePiCamera().framerate)),
            '-'],
            stdin=PIPE, stdout=PIPE, stderr=open(os.devnull, 'wb'),
            shell=False, close_fds=True)

    def write(self, b):
        self.converter.stdin.write(b)

    def read(self, nb):
        return self.converter.stdout.read1(nb)

    def flush(self):
        print('Waiting for background conversion process to exit')
        self.converter.stdin.close()
        self.converter.wait()