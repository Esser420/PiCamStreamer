import os
import sys
import time
import unittest
sys.path.append("..")
from streamer import Streamer

class MultipleOutputWriteTest(unittest.TestCase):

    def test(self):
        print("Creating 3 output files.")
        output1 = open("out1.h264", "wb")
        output2 = open("out2.h264", "wb")
        output3 = open("out3.h264", "wb")

        print("Creating Streamers with the created outputs.")
        streamer1 = Streamer("h264", id_output = ("1", output1))
        streamer2 = Streamer("h264", id_output = ("2", output2))
        streamer3 = Streamer("h264", id_output = ("3", output3))

        print("Checking if Streamer instances are same object.")
        self.assertIs(streamer1, streamer2)
        self.assertIs(streamer2, streamer3)

        print("Checking if Streamer instance has 3 outputs.")
        self.assertEqual(len(streamer1.output.outputs), 3)

        print("Recording to 3 outputs simultaneously for 5 seconds")
        streamer1.start()
        time.sleep(5)
        streamer1.stop()

        output1.close()
        output2.close()
        output3.close()

        print("Checking if 3 output files have same size.")
        self.assertEqual(os.stat("out1.h264").st_size, os.stat("out2.h264").st_size)
        self.assertEqual(os.stat("out2.h264").st_size, os.stat("out3.h264").st_size)

        print("Removing 3 output files.")
        os.remove("out1.h264")
        os.remove("out2.h264")
        os.remove("out3.h264")

if __name__ == '__main__':
    unittest.main()