import io
import picamera
import struct
import socket
from time import sleep


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

    except KeyboardInterrupt:
        print("User interrupted, closing..")
    except ConnectionRefusedError:
        print("Connection broken, closing..")
    finally:
        connection.close()
        video_socket.close()


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

            stream = io.BytesIO()
            for foo in camera.capture_continuous(stream, "jpeg", use_video_port=True):
                connection.write(struct.pack("<L", stream.tell()))
                connection.flush()
                stream.seek(0)
                connection.write(stream.read())
                stream.seek(0)
                stream.truncate()
    except Exception as e:
        # print(e)
        pass
    finally:
        try:
            connection.close()
        except BrokenPipeError:
            print("Closed from the other side")
        client_socket.close()
