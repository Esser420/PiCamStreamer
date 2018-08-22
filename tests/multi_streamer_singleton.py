import os
import sys
import time
import unittest
sys.path.append("..")
from base_streamer import BaseStreamer
from split_frame_streamer import SplitFrameStreamer
from streamer import Streamer

class MultiStreamerSingleton(unittest.TestCase):

    def test(self):
        streamer1 = Streamer("h264")
        streamer2 = Streamer("mjpeg")
        streamer3 = Streamer("yuv420")
        streamer4 = Streamer("h264", resize = "720p")

        self.assertIsNot(streamer1, streamer2)
        self.assertIsNot(streamer1, streamer3)
        self.assertIsNot(streamer1, streamer4)
        self.assertIsNot(streamer2, streamer3)
        self.assertIsNot(streamer2, streamer4)
        self.assertIsNot(streamer3, streamer4)

        self.assertIsInstance(streamer1, SplitFrameStreamer)
        self.assertIsInstance(streamer2, SplitFrameStreamer)
        self.assertIsInstance(streamer3, BaseStreamer)
        self.assertIsInstance(streamer4, SplitFrameStreamer)

        self.assertRaises(Exception, Streamer, "mjpeg", resize = "1080p")

        streamer4.ready_to_stop = True
        streamer4 = Streamer("mjpeg", resize = "1080p")

        self.assertRaises(Exception, Streamer, "mjpeg", resize = "HD")

if __name__ == '__main__':
    unittest.main()