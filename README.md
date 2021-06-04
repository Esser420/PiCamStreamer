# Deprecation Notice

This project is was mostly restructured and there is a new home for it at: https://github.com/Esser50K/PiCameleon

# PiCamStreamer
An useful abstraction layer around the PiCamera Library for the RaspberryPi

First off, the [PiCamera library](https://github.com/waveform80/picamera) is great and has the most rich documentation I've ever seen, so go check it out.

## Problems working with PiCamera

I have worked extensively with this library and have had much success in building projects with it.
Along the way I've found a couple of issues that seemed tricky to get around, this library aims to mitigate those issues.

One of the issues was that there can only be one instance of the PiCamera class because of the MMAL lock it holds,
this makes it a little tricky to use it in bigger projects as you would have to pass that object around somehow.

Another little annoyance was having to keep track of the camera's splitter ports being used.
A splitter port can be distinguished by the video/image format and resolution it uses.
If one needs to capture images at two different resolutions simultaneosly it needs to use different splitter ports.

The PiCamera library easily allows for writing the captured data to a custom output.
However, if one wants to do multiple things with the captured data it all needs to be in the same custom output class.

## Workarounds

So the first workaround was creating a Singleton wrapper for the Picamera Class. The ```SinglePiCamera```.
This lets you call the PiCamera class anywhere in the code without having to worry about the MMAL lock as it will always be the same instance.

The second workaround is done by the Streamer class.
This is a multi-singleton class that holds various instances of the streamers mapped to the splitter ports they are using.
The class manages the used splitter ports by only creating new instances when a new format&resolution combination is used.
Otherwise it returns the already created instance, hence the multi-singleton class.
This allows for the most efficient and complete usage of the camera.

The last problem is mitigated by having an ```OutputHolder``` object as the output for the Streamer instances.
This ```OutputHolder``` can hold multiple output and motion_output instances. So whenever the ```write``` or ```analyse``` 
methods are called the ```OutputHolder``` will launch a thread for every output/motion_output it holds and call the ```write``` or ```analyse``` method respectively.

### Extras

The Streamer classes can either be the ```BaseStreamer``` or the ```SplitFrameStreamer```.
The ```SplitFrameStreamer``` class is used for the ```h264``` and ```mjpeg``` formats.
The ```write``` method appends data to a buffer until a new frame is found.
This makes it possible to query the streamer for the last frame or the next one with the ```get_last_frame``` and ```get_next_frame``` methods respectively.
