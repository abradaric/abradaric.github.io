* * *
### [about me](https://abradaric.me)   |   [projects](./projects.html) | [R0A0](./r0a0.html)   |   vision (PC side) 1/N


```python
import socket
import io
import struct
from threading import Thread
from PIL import Image
from time import sleep
import zbarlight
import numpy as np
import cv2
import subprocess
from math import sqrt
```

Some familiar imports plus _Pillow, numpy, cv2_ for image processing operations. _zbarlight_ is used for reading QR codes.

```python
JPG_IMAGE = None
OFF = False
```

Couple of global vars to hold incoming jpeg image and check for shutdown signal from various functions (on this side).

```python
if cv2.ocl.haveOpenCL():

    def jpg_to_cv(jpg_img):
        return cv2.cvtColor(cv2.UMat(np.array(jpg_img)), cv2.COLOR_RGB2BGR)


else:

    def jpg_to_cv(jpg_img):
        return cv2.cvtColor(np.array(jpg_img), cv2.COLOR_RGB2BGR)
```

[OpenCL](https://opencv.org/platforms/opencl.html) in openCV with Python is really simple with [transparent API](https://www.learnopencv.com/opencv-transparent-api/) thanks to awesome devs. CUDA is a bit more complicated. Since I have AMD hardware, I haven't explored it.

```python
def network_image_stream(pc_adr, vid_port):
    global JPG_IMAGE

    server_socket = socket.socket()
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((pc_adr, vid_port))
    server_socket.listen(1)
    conn = server_socket.accept()[0].makefile("rb")
    len_size = struct.calcsize("<L")
    try:
        while True:
            if OFF:
                raise Exception
            img_len = struct.unpack("<L", conn.read(len_size))[0]
            if not img_len:
                raise Exception
            image_stream = io.BytesIO()
            image_stream.write(conn.read(img_len))
            image_stream.seek(0)
            JPG_IMAGE = Image.open(image_stream)
    except Exception as e:
        #print(e)
        print("Global OFF or broken from the other side")
    finally:
        conn.close()
        server_socket.close()
```

Let's get some video feed so we can analyse it. We create a TCP socket and wait for the client to connect. We make a file-like interface for connection. As mentioned before, len\_size is little endian unsigned long piece of data which tells us how many bytes we need to read (which is size of jpeg image). Then in while-loop first we check for the global OFF signal. If there isn't one, we go on. We read exactly how many bytes is the size of image, then create BytesIO stream in memory. In that stream we write bytes which we read from connection, which is image data. Then we rewind the stream, and write the image in global variable aptly named JPG\_IMAGE. Loop will break either on OFF signal (on this side) or on eventual problems on the other end.


```python
def get_filler_frames(vid):
    sequence = cv2.VideoCapture(vid)
    frames = []
    while True:
        ack, frame = sequence.read()
        if not ack:
            break
        frames.append(frame)
    return frames
```

Establishing video feed is never done instantly. This function loads some animation to loop until connection is established. Parameter can be either gif image or mp4 video, anything iterable really.


```python
def cv_start(pc_adr, vid_port):
    global OFF
    t1 = Thread(target=network_image_stream, args=(pc_adr, vid_port))
    t1.start()
    filler_frames = get_filler_frames("matrix2.mp4")
    cv2.namedWindow("Frame", cv2.WINDOW_NORMAL)
    while True:
        for frame in filler_frames:
            cv2.imshow("Frame", frame)
            cv2.waitKey(35)
        if JPG_IMAGE:
            break

    detect_faces, detect_humans = False, False
    read_qr = False
```

Let's start with the module entry point aka its _main_ function. Reading incoming jpeg images will be run as threaded function. In python _multiprocessing_ module is used for real parallelism. Threads from _threading_ module are preemptive threads (good for I/O tasks), and they run concurrently (due to [GIL](https://wiki.python.org/moin/GlobalInterpreterLock). There are also coroutines (_asyncio_ module), but I digress. I've chosen green characters on black background for looping animation until the data arrives. Then we create the window and show the animation at least once. When the image arrives, we break out of the loop. Also, for now we won't detect anything. More about that in part two.

```python
    while True:

        frame = jpg_to_cv(JPG_IMAGE)

        # ...
        # ...
        # processing code is here
        # not _that_much_ of it
        # but enough that it deserves
        # its own post
        # ...
        # ...

        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1)

        if key == ord("q"):
            OFF = True
            cv2.destroyAllWindows()
            break
```

More about detecting and counting objects in another post. When we press _q_, program will destroy cv2 window and shut down incoming data stream.
