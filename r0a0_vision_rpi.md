* * *
### [about me](https://abradaric.me)   |   [projects](./projects.html) | [R0A0](./r0a0.html)   |   vision (RPi side)

If you just want the code for this module, [here](./rpi_vision.py) you go. BTW, [picamera docs](https://picamera.readthedocs.io/en/latest/index.html) is awesome resource! This is 99% from there.

```python
import io
import picamera
import struct
import socket
from time import sleep
```

Imports from standard library, plus picamera. Don't forget [pipenv setup](./r0a0_python.html).

```python
def cv_start(pc_adr, vid_port):
    client_socket = socket.socket()
    while True:
        try:
            client_socket.connect((pc_adr, vid_port))
        except Exception as e:
            # print(e)
            sleep(0.1)
            continue
        break
```

First, let's connect to the server where computer vision operations will be executed. Keep trying to connect until it happens, and then break out of the loop. BTW, print statements are debugging leftovers. On eventual refactoring I'll get rid of them.

```python
    connection = client_socket.makefile("wb")
    try:
        with picamera.PiCamera() as camera:
            camera.resolution = (320, 240)
            camera.framerate = 30
            camera.exposure_mode = "sports"
            camera.vflip = True
            camera.hflip = True
            camera.start_preview()
            sleep(2)
```

We'll make a file-like interface out of connection to simplify writing data. Some standard settings, check all options [here](https://picamera.readthedocs.io/en/latest/api_camera.html). You may not need _vflip_ and/or _hflip_, depending how you orientate camera on the robot. Sensor's _sports_  exposure mode is to automatically remove motion blur on turning, very useful. You may experiment with resolution, depending on your server computing power. Sleep is because sensors needs a while to adjust to light.

```python
            stream = io.BytesIO()
            for foo in camera.capture_continuous(stream, "jpeg", use_video_port=True):
                connection.write(struct.pack("<L", stream.tell()))
                connection.flush()
                stream.seek(0)
                connection.write(stream.read())
                stream.seek(0)
                stream.truncate()
```

We then construct in-memory stream to hold the image. Video port is used to keep shutter from closing and opening for every frame. Let's digest this piece by piece. stream.tell() tells us position in the stream, which translates to how many bytes are there in the stream, which means how big is the image. We pack the information as little-endian unsigned long ("_<L_") (read more [here](https://docs.python.org/3/library/struct.html)). Then, we make sure it gets sent (flush). We do this because not every image is the same size. Same resolution yes, but not size in bytes. On the server side first that information will be read, then server will know how many bytes exactly to read to get image data. Read a bit about [data compression](https://en.wikipedia.org/wiki/Data_compression), and [jpeg](https://en.wikipedia.org/wiki/JPEG) specifically. After that we rewind the stream (_seek()_), and send the image itself (_connection.write(stream.read())_). Then we rewind it again and clear it for the next image.

```python
    except Exception as e:
        # print(e)
        pass
    finally:
        try:
            connection.close()
        except BrokenPipeError:
            print("Closed from the other side")
        client_socket.close()
```

Last but not least, cleaning. That's it for the JPEG transfer. We can also send [h264](https://en.wikipedia.org/wiki/H.264/MPEG-4_AVC) video.

```python
def h264_start(pc_adr, vid_port):
    video_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        try:
            video_socket.connect((pc_adr, vid_port))
        except Exception as e:
            # print(e)
            sleep(0.1)
            continue
        break
```

We use UDP for this one. It's for free-drive, without openCV operations.

```python
    connection = video_socket.makefile("wb")
    try:
        with picamera.PiCamera() as camera:
            camera.resolution = (640, 480)
            camera.framerate = 60
            camera.vflip = True
            camera.hflip = True
            camera.exposure_mode = "auto"
            camera.start_preview()
            sleep(2)
            camera.start_recording(connection, format="h264")
            print("Started looking..")
            camera.wait_recording(600)
            camera.stop_recording()
```

We can afford bigger resolution and fps. Sensor exposure mode is "auto", for better light adjustment. h264 video is written to a file-like connection interface, just like before. But we set a 10 minutes timer here, in case someone gets carried away with free-drive.

```python
    except KeyboardInterrupt:
        print("User interrupted, closing..")
    except ConnectionRefusedError:
        print("Connection broken, closing..")
    finally:
        connection.close()
        video_socket.close()
```

Finally, cleaning up.

Also, it's possible to send openCV objects directly over the network. Read more [this](https://picamera.readthedocs.io/en/latest/recipes2.html#capturing-to-an-opencv-object) and [that](https://picamera.readthedocs.io/en/latest/api_array.html). But, it's a lot of overhead on the network.
