* * *
### [about me](https://abradaric.me)   |   [projects](./projects.html) | [R0A0](./r0a0.html)   |   vision (PC side)


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
FRONTAL_FACE_DETECTOR = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)
SIDE_FACE_DETECTOR = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_profileface.xml"
)
LOWER_BODY_DETECTOR = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_lowerbody.xml"
)
FULL_BODY_DETECTOR = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_fullbody.xml"
)
UPPER_BODY_DETECTOR = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_upperbody.xml"
)

JPG_IMAGE = None
OFF = False
```

If you installed openCV via pip, this is the way you load library included Haar-cascade classifiers, as can be seen [here](https://pypi.org/project/opencv-python/). More about them below. Also, couple of global vars.

```python
if cv2.ocl.haveOpenCL():

    def jpg_to_cv(jpg_img):
        return cv2.cvtColor(cv2.UMat(np.array(jpg_img)), cv2.COLOR_RGB2BGR)


else:

    def jpg_to_cv(jpg_img):
        return cv2.cvtColor(np.array(jpg_img), cv2.COLOR_RGB2BGR)
```

OpenCL in openCV with Python is really simple with [transparent API](https://www.learnopencv.com/opencv-transparent-api/) thanks to awesome devs.

```python
def write_text(img, text):
    x = 5
    y = 15
    for line in text:
        cv2.putText(
            img,
            (line),
            (x, y),
            cv2.FONT_HERSHEY_PLAIN,
            1.0,
            (0, 0, 0),
            thickness=1,
            lineType=cv2.LINE_AA,
        )
        y += 15
```

One of helper functions. Here we simply pass in the frame on which we want to write on, and list of lines we want to write. Lines will be in the upper left corner, starting at (5, 15). Next one will be (5, 30) etc.

```python
def draw_boxes(img, objects):
    for obj in objects:
        for x, y, w, h in obj:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
```

When we detect various objects, we want to mark them. Another simple helper function, parameters are frame on which we draw and list of detected objects. These detected objects are basically rectangles in the form of tuples containing x and y coordinate of upper left point and width and height. Hence x,y,w,h. Therefore we will draw rectangle around them.

```python
def get_faces(gray_img):
    frontal_faces = FRONTAL_FACE_DETECTOR.detectMultiScale(gray_img)
    side_faces = SIDE_FACE_DETECTOR.detectMultiScale(gray_img)
    return frontal_faces, side_faces


def get_humans(gray_img):
    legs = LOWER_BODY_DETECTOR.detectMultiScale(gray_img)
    full_body = FULL_BODY_DETECTOR.detectMultiScale(gray_img)
    upper_body = UPPER_BODY_DETECTOR.detectMultiScale(gray_img)
    return legs, upper_body, full_body
```

Haar-cascade based detectors are very fast. Not as accurate as some other solutions like neural networks, but a lot faster, and usually accurate enough. Read more [here](https://docs.opencv.org/3.4/d7/d8b/tutorial_py_face_detection.html), or watch this [video](https://www.youtube.com/watch?v=uEJ71VlUmMQ). You can even [train your own](https://docs.opencv.org/3.4/dc/d88/tutorial_traincascade.html).

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
        #print(e) #debugging leftovers, will get rid off on _eventual_ refactoring
        print("Global OFF or broken from the other side")
    finally:
        conn.close()
        server_socket.close()
```

Of course we need images to be able to analyse them. We create a TCP socket and wait for the client to connect. We make a file-like interface for connection. As mentioned before, len\_size is little endian unsigned long piece of data which tells us how many bytes we need to read (which is size of jpeg image). Then in while-loop first we check for the global OFF signal. If there isn't one, we go on. We read exactly how many bytes is the size of image, then create BytesIO stream in memory. In that stream we write bytes which we read from connection, which is image data. Then we rewind the stream, and write the image in global var aptly named JPG\_IMAGE. Loop will break either on OFF signal (on this side) or on eventual problems on the other end.

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

Establishing video feed is never done instantly. Hence another helper function, which loads some animation to loop until connection is established. Parameter can be either gif image or mp4 video, anything iterable really. I've chosen green characters on black blackground from Matrix.

```python
def count_objects(objects, scale):
    centroids = []
    for obj in objects:
        for x, y, w, h in obj:
            centroid = (x + (w / 2), y + (h / 2), sqrt(w ** 2 + h ** 2) / 2 * scale)
            centroids.append(centroid)
    centroids = clean_centroids(centroids)
    return centroids
```

Let's say we want to count certain objects, like faces for example.


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

Let's start with _the main_ function aka entry point. Reading incoming jpeg images will be run as a thread. Then we load filler frames. In this case, matrix sequence. Create the window, and show the sequence _at least_ once. If image has arrived, break out of the loop and proceed. Else, keep looping sequence until the image has arrived. Default state will be just showing image on screen, without performing any detections.

```python
    while True:

        frame = jpg_to_cv(JPG_IMAGE)

        if detect_faces or detect_humans:
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if detect_faces:
                faces, profiles = get_faces(gray_frame)
                heads = count_objects([faces, profiles], scale=0.75)
                draw_circles(frame, heads)
            if detect_humans:
                legs, torso, bodies = get_humans(gray_frame)
                num_bodies = count_objects([legs, torso, bodies], scale=1.2)
                draw_boxes(frame, [legs, torso, bodies])
```

First we transform jpeg image to something openCV can use.
















































































