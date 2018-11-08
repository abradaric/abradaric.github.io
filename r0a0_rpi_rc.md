* * *
### [about me](https://abradaric.me)   |   [projects](./projects.html) | [R0A0](./r0a0.html)   |   remote control (RPi side)

```python
import socket
import RPi.GPIO as GPIO
```

In addition to socket module from standard library, we need something to work with GPIO pins. [RPi.GPIO](https://pypi.org/project/RPi.GPIO/) will do just fine, in spite of "_..Note that the current release does not support SPI, I2C, hardware PWM or serial functionality on the RPi yet._". For some advanced usage [pigpio](http://abyz.me.uk/rpi/pigpio/index.html) is recommended, with its python [interface](http://abyz.me.uk/rpi/pigpio/python.html).

First things first, we declare the pins we're using.

```python
GPIO.setmode(GPIO.BOARD)
GPIO.setup(36, GPIO.OUT)
GPIO.setup(33, GPIO.OUT)
GPIO.setup(35, GPIO.OUT)
GPIO.setup(37, GPIO.OUT)
GPIO.setup(38, GPIO.OUT)
GPIO.setup(40, GPIO.OUT)

LEFT_SPEED = GPIO.PWM(35, 1000)
RIGHT_SPEED = GPIO.PWM(33, 1000)
```

You can use either _BOARD_ layout or _BCM_ layout.

![Branching](https://i.imgur.com/NZe70aK.png)

Basically, _BOARD_ pin numbering is by order on board itself, _BCM_ is by some chip spec, which you have to look up. Pins can be declared either IN (input) or OUT (output). They operate on 3.3V, so be careful when connecting various sensors which operate on 5V. In that case one can use either [logic level converter](https://ebay.to/2Plm8aR) (_upgrades, additional sensors_) or construct circuits with resistors (on breadboard). On the other hand, if pin is declared as output, and something on the other side operates at 5V, it should all work fine, because 3.3V is high enough to be interpreted as HIGH signal. Basically, [0V,2.5V] = LOW, [2.5V,5V] = HIGH.

Pins 36 and 38 control the direction of left motor, pins 37 and 40 direction of right motor. Pins 35 and 33 control the speed of left and right motor (software [PWM](https://en.wikipedia.org/wiki/Pulse-width_modulation), which is not an issue for DC motors).

```python
NEUTRAL = 0
FIRST = 40
SECOND = 50
THIRD = 60
FOURTH = 70
FIFTH = 90

GEARBOX = (FIRST, SECOND, THIRD, FOURTH, FIFTH)
GEAR = 0

DIRECTIONS = ("E", "NE", "N", "NW", "W", "SW", "S", "SE")
```

Speed is in [0,100], which is [duty cycle](https://en.wikipedia.org/wiki/Duty_cycle) of PWM signal. Directions are _east_, _north-east etc_. For example, _north_ is straight ahead, _east_ is rotation clockwise, _north-east_ is slightly turning to the right. Note, this is for model build 0.1, which doesn't have servo motors. It turns by running engines in opposite directions and/or different speeds.

![Branching](https://upload.wikimedia.org/wikipedia/commons/0/02/PWM_duty_cycle_with_label.gif)

```python
def shift_up():
    global GEAR
    if GEAR == 4:
        print("FIFTH GEAR")
    else:
        print(f"GEAR {GEARBOX[GEAR]} --> {GEARBOX[GEAR+1]}")
        GEAR += 1


def shift_down():
    global GEAR
    if GEAR == 0:
        print("FIRST GEAR")
    else:
        print(f"GEAR {GEARBOX[GEAR]} --> {GEARBOX[GEAR-1]}")
        GEAR -= 1
```

GEAR is global variable here. In Python, any referenced variable is implicitly global. If you modify value of a variable, it's implicitly local. If you want to modify global variable, you have to explicitly use the keyword _global_ to declare it as such. Anyway, GEAR is index of speed level (GEARBOX).

```python
def left_engine(mode, speed):
    if mode == "D":
        GPIO.output(38, False)
        GPIO.output(36, True)
    elif mode == "R":
        GPIO.output(38, True)
        GPIO.output(36, False)
    elif mode == "N":
        GPIO.output(38, False)
        GPIO.output(36, False)
    LEFT_SPEED.start(speed)


def right_engine(mode, speed):
    if mode == "D":
        GPIO.output(37, False)
        GPIO.output(40, True)
    elif mode == "R":
        GPIO.output(37, True)
        GPIO.output(40, False)
    elif mode == "N":
        GPIO.output(37, False)
        GPIO.output(40, False)
    RIGHT_SPEED.start(speed)
```

Function for each motor. Modes are "D" (_drive_), "R" (_reverse_) and "N" (_neutral_).

```python
def drive(direction):
    if direction == "N":
        left_engine("D", GEARBOX[GEAR])
        right_engine("D", GEARBOX[GEAR])
    elif direction == "S":
        left_engine("R", GEARBOX[GEAR])
        right_engine("R", GEARBOX[GEAR])
    elif direction == "E":
        left_engine("D", GEARBOX[GEAR])
        right_engine("R", GEARBOX[GEAR])
    elif direction == "W":
        left_engine("R", GEARBOX[GEAR])
        right_engine("D", GEARBOX[GEAR])
    elif direction == "SW":
        left_engine("R", slower(GEARBOX[GEAR]))
        right_engine("R", GEARBOX[GEAR])
    elif direction == "SE":
        left_engine("R", GEARBOX[GEAR])
        right_engine("R", slower(GEARBOX[GEAR]))
    elif direction == "NW":
        left_engine("D", (GEARBOX[GEAR]))
        right_engine("D", slower(GEARBOX[GEAR]))
    elif direction == "NE":
        left_engine("D", slower(GEARBOX[GEAR]))
        right_engine("D", (GEARBOX[GEAR]))
```

High level function which makes the engines run based on message it receives from the other end of connection. Message can be one of elements in _DIRECTIONS_. Notice _slower()_ speed when turning slightly. As mentioned, turning is achieved by running engines at different speeds.

```python
def slower(speed):
    if speed == FIRST:
        return speed - 25
    elif speed == SECOND:
        return speed - 35
    else:
        return speed * 0.5
```

Robot needs to rest once in a while.

```python
def neutral():
    global GEAR
    left_engine("N", NEUTRAL)
    right_engine("N", NEUTRAL)
    GEAR = 0
```

Puts the engines in neutral and resets the speed.

And of course, robot needs input for this _WASD_ driving mode.

```python
def start(rasp_addr, comm_port):
    comm_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    comm_socket.bind((rasp_adr, comm_port))

    while True:
        data = comm_socket.recv(64)
        if not data:
            break
        command = data.decode()
        print(f"Command: {command}")
        if command == "q":
            LEFT_SPEED.stop()
            RIGHT_SPEED.stop()
            print("Shutting down")
            break
        if command == "SHIFT_UP":
            shift_up()
        elif command == "SHIFT_DOWN":
            shift_down()
        if command in DIRECTIONS:
            drive(command)
        elif command == "NEUTRAL":
            neutral()

    comm_socket.close()
    GPIO.cleanup()
```

That's it for the RPi side of _WASD_ free-driving mode.
