import socket
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setup(36, GPIO.OUT)
GPIO.setup(33, GPIO.OUT)
GPIO.setup(35, GPIO.OUT)
GPIO.setup(37, GPIO.OUT)
GPIO.setup(38, GPIO.OUT)
GPIO.setup(40, GPIO.OUT)

LEFT_SPEED = GPIO.PWM(33, 1000)
RIGHT_SPEED = GPIO.PWM(35, 1000)

NEUTRAL = 0
FIRST = 40
SECOND = 50
THIRD = 60
FOURTH = 70
FIFTH = 90

GEARBOX = (FIRST, SECOND, THIRD, FOURTH, FIFTH)
GEAR = 0

DIRECTIONS = ("E", "NE", "N", "NW", "W", "SW", "S", "SE")


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
    RIGHT_SPEED.start(speed)


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
    LEFT_SPEED.start(speed)


def slower(speed):
    if speed == FIRST:
        return speed - 25
    elif speed == SECOND:
        return speed - 35
    else:
        return speed * 0.5


def neutral():
    global GEAR
    left_engine("N", NEUTRAL)
    right_engine("N", NEUTRAL)
    GEAR = 0


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


def start(rasp_adr, comm_port):
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
