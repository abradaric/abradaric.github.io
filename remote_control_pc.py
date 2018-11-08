import socket
from threading import Thread
from time import sleep
from pynput.keyboard import KeyCode, Listener


FORWARD = KeyCode.from_char("'w'")
BACKWARD = KeyCode.from_char("'s'")
LEFT = KeyCode.from_char("'a'")
RIGHT = KeyCode.from_char("'d'")
QUIT = KeyCode.from_char("'q'")
SHIFT_DOWN = KeyCode.from_char("'j'")
SHIFT_UP = KeyCode.from_char("'i'")
COMBINATION = (FORWARD, BACKWARD, LEFT, RIGHT, QUIT, SHIFT_DOWN, SHIFT_UP)


def start(rasp_adr, motor_port):

    comm_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    comm_socket.connect((rasp_adr, motor_port))
    pressed_buttons = set()

    def neutral():
        while True:
            sleep(0.2)
            if not comm_socket:
                break
            if not pressed_buttons:
                try:
                    comm_socket.send("NEUTRAL".encode())
                except Exception as e:
                    pass

    def send_comms():
        if QUIT in pressed_buttons:
            print("Shutting down!")
            while True:
                try:
                    comm_socket.send("q".encode())
                except Exception as e:
                    break

        if SHIFT_DOWN in pressed_buttons:
            comm_socket.send("SHIFT_DOWN".encode())
        elif SHIFT_UP in pressed_buttons:
            comm_socket.send("SHIFT_UP".encode())

        if FORWARD in pressed_buttons and RIGHT in pressed_buttons:
            comm_socket.send("NE".encode())
        elif FORWARD in pressed_buttons and LEFT in pressed_buttons:
            comm_socket.send("NW".encode())
        elif BACKWARD in pressed_buttons and LEFT in pressed_buttons:
            comm_socket.send("SW".encode())
        elif BACKWARD in pressed_buttons and RIGHT in pressed_buttons:
            comm_socket.send("SE".encode())
        elif RIGHT in pressed_buttons:
            comm_socket.send("E".encode())
        elif FORWARD in pressed_buttons:
            comm_socket.send("N".encode())
        elif BACKWARD in pressed_buttons:
            comm_socket.send("S".encode())
        elif LEFT in pressed_buttons:
            comm_socket.send("W".encode())

    def on_press(key):
        if KeyCode.from_char(key) in COMBINATION:
            pressed_buttons.add(KeyCode.from_char(key))
        send_comms()

    def on_release(key):
        try:
            if QUIT in pressed_buttons:
                send_comms()
                listener.stop()
            else:
                pressed_buttons.remove(KeyCode.from_char(key))
                send_comms()
        except KeyError:
            pass

    t2 = Thread(target=neutral)
    t2.start()
    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
    comm_socket.close()
    print("Command stream shut down")
