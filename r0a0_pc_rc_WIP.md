* * *
### [about me](https://abradaric.me)   |   [projects](./projects.html) | [R0A0](./r0a0.html)   |   remote control (PC side)

If you just want the code for this module, [here](./remote_control_pc.py) you go.

BTW, this one is kinda ugly, I'll probably refactor at some point. Anyway, imports first. Most stuff from standard library, plus [pynput](https://github.com/moses-palmer/pynput) for monitoring keyboard input.

```python
FORWARD = KeyCode.from_char('w')
BACKWARD = KeyCode.from_char('s')
LEFT = KeyCode.from_char('a')
RIGHT = KeyCode.from_char('d')
QUIT = KeyCode.from_char('q')
SHIFT_DOWN = KeyCode.from_char('j')
SHIFT_UP = KeyCode.from_char('i')

COMBINATION = (FORWARD, BACKWARD, LEFT, RIGHT, QUIT, SHIFT_DOWN, SHIFT_UP)
```

We put the relevant keys (keycodes) in a tuple for membership checking on each key press.

```python
PRESSED = set()

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

```

We construct a [set](https://docs.python.org/3.7/tutorial/datastructures.html?highlight=set#sets). _A set is an unordered collection with no duplicate elements._ So if you're holding _W_, only one element will be put in the set. If you tried this with a list, you would get into trouble.
