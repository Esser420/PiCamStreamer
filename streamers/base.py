"""
BaseStreamer is the base class for generic streamer implementations.
"""
from utils.single_picamera import SinglePiCamera
from outputs.output_holder import WriterOutputHolder
from outputs.motion_output_holder import MotionOutputHolder
from threading import Thread

class BaseStreamer:
    def __init__(self, port, format, resize, options):
        self.camera = SinglePiCamera()
        self.port = port
        self.format = format
        self.resize = resize
        self.output = WriterOutputHolder()
        self.motion_output = MotionOutputHolder(size = resize)
        self.sub_output = None
        self.options = options
        self.ready_to_stop = False
        self.is_running = False

    def close(self):
        self.camera.stop_recording(splitter_port = self.port)

    def stop(self, wait = True):
        if self.ready_to_stop:
            return

        self.ready_to_stop = True
        self._teardown_streamer()
        self.close()
        self.is_running = False

    def start(self):
        if not self.is_running:
            self._setup_streamer()
            if type(self.output) is WriterOutputHolder:
                self.output.start()
            self.run_streamer()
            self.is_running = True

    def run_streamer(self):
        output = self.sub_output if self.sub_output else self.output
        print("Start recording with %s format, size: %s, on port %d" % (self.format, str(self.resize), self.port))
        self.camera.start_recording(output, 
                                    motion_output = self.motion_output,
                                    format = self.format,
                                    splitter_port = self.port,
                                    resize = self.resize,
                                    **self.options)

    def wait_recording(self, seconds):
        self.camera.wait_recording(seconds, self.port)

    def split_recording(self, output):
        """
        Only use this method if you have changed the default output of OutputHolder
        """
        self.camera.split_recording(output, splitter_port = self.port)
        self.output = output

    def rebind_output(self, output_id, output):
        self.output.prepare_new_output(output_id, output)
        self.camera.split_recording(self.output, splitter_port = self.port)
        self.output.notify_split()
        
    def _setup_streamer(self):
        pass

    def _teardown_streamer(self):
        pass
