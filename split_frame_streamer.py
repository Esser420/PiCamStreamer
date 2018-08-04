import io
import struct
from threading import Thread, Event
from base_streamer import BaseStreamer

SPLITTER_STRINGS = {
    "mjpg": b'\xff\xd8',
    "h264": b'\x00\x00\x00\x01'
}

class SplitFrameStreamer(BaseStreamer):
    def __init__(self, camera, port, format, resolution, append_size = False, options = {}):
        super().__init__(camera, port, format, resolution, options)
        self.event = Event()
        self.append_size = append_size
        self.stream = io.BytesIO()
        self.last_frame = None
        self.streamer_thread = None
        self.splitter_string = SPLITTER_STRINGS[format]

    def setup_streamer(self):
        self.sub_output = self
        if self.output:
            self.streamer_thread = Thread(target = self.stream_frames)
            self.streamer_thread.start()

    def get_last_frame(self):
        return self.last_frame

    def get_next_frame(self, timeout = None):
        if self.event.wait(timeout):
            return self.last_frame

    def stream_frames(self):
        while not self.ready_to_stop:
            frame = self.get_next_frame()
            size = len(frame)
            if self.append_size:
                self.output.write(struct.pack('<L', size))
            self.output.write(frame)

    def write(self, buf):
        if buf.startswith(self.splitter_string):
            if self.stream.tell() > 0:
                self.last_frame = self.stream.getvalue()
                self.event.set()
                self.stream.seek(0)
                self.stream.truncate()
        self.stream.write(buf)
        self.event.clear()

    def teardown_streamer(self):
        self.streamer_thread.join()
