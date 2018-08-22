"""
Generic Streamer Class that returns one of the implementations of base_streamer.
It also works as a multi-singleton class as it will only create new Streamer instances if they have a new output format or resolution
Different outputs can be appended to the same streamer instance.

If the formats "h264" or "mjpeg" are set then it will return a SplitFrameStreamer which streams a frame at a time.
All other formats return an instance of BaseStreamer which produces raw streams.
"""
import os
from .base import BaseStreamer
from .split_frame import SplitFrameStreamer
from .ffmpeg import FFMPEGStreamer
from utils.single_picamera import SinglePiCamera

ROOT_PATH = '{0}/../'.format(os.path.dirname(os.path.abspath(__file__)))
SPLIT_FRAME_FORMATS = ("mjpeg", "h264")
FFMPEG = "mpeg"

def get_streamer_instance(port, format, resolution, append_size, split_frames, recording_options):
    if format in SPLIT_FRAME_FORMATS and split_frames:
        return SplitFrameStreamer(port, format, resolution, append_size, options = recording_options)
    elif format == FFMPEG:
        return FFMPEGStreamer(port, resolution, options = recording_options)
    else:
        return BaseStreamer(port, format, resolution, options = recording_options)

class Streamer:
    _available_ports = [0, 1, 2, 3]
    _streamers = {}
    _portmap = {}

    def __new__(cls, format,
                     id_output = (None, None),
                     id_motion_output = (None, None),
                     resize = None,
                     append_size = False,
                     split_frames = True,
                     recording_options = {}):
        resolution = resize if resize else SinglePiCamera().resolution
        res_str = "_".join(map(str, resolution))
        port_key = "%s_%s_%s" % (format, res_str, str(split_frames))
        outID, output = id_output[0], id_output[1]
        moutID, motion_output = id_motion_output[0], id_motion_output[1]
        if port_key in cls._streamers.keys():
            streamer = cls._streamers[port_key]
            if output:
                streamer.output.add_output(outID, output)
            if motion_output:
                streamer.motion_output.add_output(moutID, motion_output)
            return streamer
        
        # Try cleaning up streamers and recovering ports
        elif len(cls._available_ports) == 0:
            to_stop = []
            for key, streamer in cls._streamers.items():
                if streamer.ready_to_stop:
                    to_stop.append(key)

            for key in to_stop:
                cls._streamers[key].stop()
                del cls._streamers[key]
                cls._available_ports.append(cls._portmap[key])
                del cls._portmap[key]

            # Check again
            if len(cls._available_ports) == 0:
                raise Exception("No more camera ports available for new streamer")
            
        port = cls._available_ports.pop(0)
        new_streamer = get_streamer_instance(port, format, resolution, append_size, split_frames, recording_options)
        if output and outID:
            new_streamer.output.add_output(outID, output)
        if motion_output and moutID:
            new_streamer.motion_output.add_output(moutID, motion_output)

        cls._streamers[port_key] = new_streamer
        cls._portmap[port_key] = port
        return new_streamer