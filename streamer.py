"""
Generic Streamer Class that returns one of the implementations of base_streamer.
It also works as a multi-singleton class as it will only create new Streamer instances if they have a new output format or resolution
Different outputs can be appended to the same streamer instance.

If the formats "h264" or "mjpg" are set then it will return a SplitFrameStreamer which streams a frame at a time.
All other formats return an instance of BaseStreamer which produces raw streams.
"""
from base_streamer import BaseStreamer
from split_frame_streamer import SplitFrameStreamer
from utils.single_picamera import SinglePiCamera

SPLIT_FRAME_FORMATS = ("mjpg", "h264")

def get_streamer_instance(port, format, resolution, append_size, recording_options):
    if format in SPLIT_FRAME_FORMATS:
        return SplitFrameStreamer(SinglePiCamera(), port, format, resolution, append_size, options = recording_options)
    else:
        return BaseStreamer(SinglePiCamera(), port, format, resolution, options = recording_options)

class Streamer:
    _available_ports = [0, 1, 2, 3]
    _streamers = {}
    _portmap = {}

    def __new__(cls, format, id_output = (None, None), id_motion_output = (None, None), resize = None, append_size = False, recording_options = {}):
        resolution = resize if resize else SinglePiCamera().resolution
        res_str = "_".join(map(str, resolution))
        port_key = "%s_%s" % (format, res_str)
        outID, output = id_output
        moutID, motion_output = id_motion_output
        if port_key in cls._streamers.keys():
            streamer = cls._streamers[port_key]
            if output:
                streamer.output.add_output(outID, output)
            if motion_output:
                streamer.output.add_motion_output(moutID, motion_output)
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
        new_streamer = get_streamer_instance(port, format, resolution, append_size, recording_options)
        if output and outID:
            new_streamer.output.add_output(outID, output)
        if motion_output and moutID:
            new_streamer.output.add_motion_output(moutID, motion_output)

        cls._streamers[port_key] = new_streamer
        cls._portmap[port_key] = port
        return new_streamer