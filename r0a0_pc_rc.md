* * *
### [about me](https://abradaric.me)   |   [projects](./projects.html) | [R0A0](./r0a0.html)   |   remote control (PC side)

If you just want the code for this module, [here](./remote_control_pc.py) you go.

```python
import socket
from threading import Thread
from time import sleep
from pynput.keyboard import KeyCode, Listener
```

Imports first. Some stuff from standard library, plus [pynput](https://github.com/moses-palmer/pynput) for monitoring keyboard input.

```python
FORWARD = KeyCode.from_char('w')
BACKWARD = KeyCode.from_char('s')
LEFT = KeyCode.from_char('a')
RIGHT = KeyCode.from_char('d')
QUIT = KeyCode.from_char('q')
SHIFT_DOWN = KeyCode.from_char('j')
SHIFT_UP = KeyCode.from_char('i')
COMBINATION = (FORWARD, BACKWARD, LEFT, RIGHT, QUIT, SHIFT_DOWN, SHIFT_UP)

COMM_SOCK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
PRESSED = set()
```

We put the relevant keys (keycodes) in a tuple for membership checking on each key press. We create UDP socket and construct a [set](https://docs.python.org/3.7/tutorial/datastructures.html?highlight=set#sets) for putting pressed keys in. _A set is an unordered collection with no duplicate elements._ So if you're holding _W_, only one element will be put in the set. If you tried this with a list, you would get into trouble.

```python
def on_press(key):
    if KeyCode.from_char(key) in COMBINATION:
        PRESSED.add(KeyCode.from_char(key))
    send_comms()


def on_release(key):
    try:
        if QUIT in PRESSED:
            send_comms()
            KEYBOARD_LISTENER.stop()
        else:
            PRESSED.remove(KeyCode.from_char(key))
            send_comms()
    except KeyError:
        pass


KEYBOARD_LISTENER = Listener(on_press=on_press, on_release=on_release)
```

When a key is pressed, it is checked if it's relevant, if it is it gets added to _PRESSED_, and state gets sent. On release first _try-except_ is for some special problems (Ctrl, Alt etc). Also, it checks for "_Q_", which quits the program. We construct a listener (it's a thread), but we don't start it yet.

```python
def neutral():
    while True:
        sleep(0.2)
        if not COMM_SOCK:
            break
        if not PRESSED:
            try:
                COMM_SOCK.send("NEUTRAL".encode())
            except Exception as e:
                # print(e)
                pass
```

This function will also be run as a thread. Periodically it will send message "NEUTRAL" if no keys are pressed.

```python
def send_comms():
    if QUIT in PRESSED:
        print("Shutting down!")
        while True:
            try:
                COMM_SOCK.send("q".encode())
            except Exception as e:
                # print(e)
                break

    if SHIFT_DOWN in PRESSED:
        COMM_SOCK.send("SHIFT_DOWN".encode())
    elif SHIFT_UP in PRESSED:
        COMM_SOCK.send("SHIFT_UP".encode())

    if FORWARD in PRESSED and RIGHT in PRESSED:
        COMM_SOCK.send("NE".encode())
    elif FORWARD in PRESSED and LEFT in PRESSED:
        COMM_SOCK.send("NW".encode())
    elif BACKWARD in PRESSED and LEFT in PRESSED:
        COMM_SOCK.send("SW".encode())
    elif BACKWARD in PRESSED and RIGHT in PRESSED:
        COMM_SOCK.send("SE".encode())
    elif RIGHT in PRESSED:
        COMM_SOCK.send("E".encode())
    elif FORWARD in PRESSED:
        COMM_SOCK.send("N".encode())
    elif BACKWARD in PRESSED:
        COMM_SOCK.send("S".encode())
    elif LEFT in PRESSED:
        COMM_SOCK.send("W".encode())
```

Function that sends messages is simple. It just checks what's in _PRESSED_ set and sends according message. Message is one of the elements in _DIRECTIONS_ ("NW", "SW" etc), gear shift or QUIT. QUIT will be repeatedly sent until it is interpreted on the other side and socket gets closed.

```python
def start(rasp_adr, motor_port):
    KEYBOARD_LISTENER.start()
    COMM_SOCK.connect((rasp_adr, motor_port))
    t2 = Thread(target=neutral)
    t2.start()
    KEYBOARD_LISTENER.join()
    COMM_SOCK.close()
    print("Command stream shut down")
```

Finally, the functions that gets called from the main module. It connects to the RPi, starts the threads and waits for the listener to stop. It stops when you press "Q", and then it closes the socket. That's it for the _WASD_ mode PC side!
