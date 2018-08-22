from threading import Thread
from .base import BaseStreamer
from outputs.ffmpeg import FFMPEGOutput

CHUNK_SIZE = 32768

class FFMPEGStreamer(BaseStreamer):
    def __init__(self, port, resolution, options = {}):
        super().__init__(port, "yuv", resolution, options)
    
    def _setup_streamer(self):
        self.sub_output = FFMPEGOutput()
        self.sub_output.start_ffmpeg_converter()
        if self.output:
            self.streamer_thread = Thread(target = self.stream_chunks)
            self.streamer_thread.start()

    def stream_chunks(self, chunk_size = CHUNK_SIZE):
        while not self.ready_to_stop:
            chunk = self.sub_output.read(chunk_size)
            self.output.write(chunk)

    def _teardown_streamer(self):
        self.sub_output.flush()
        self.streamer_thread.join()