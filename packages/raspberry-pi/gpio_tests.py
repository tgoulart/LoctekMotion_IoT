import serial

from gpiozero import Device, LED
from time import sleep

def gpio_tests():
    print(Device.pin_factory)

    tx = LED("GPIO14")

    print(Device.pin_factory)
    print(tx.pin_factory)

    print(tx.value)
    tx.on()
    print(tx.value)
    sleep(1)
    print(tx.value)


def serial_tests():
    # ser = serial.serial_for_url("loop://")
    ser = serial.Serial("/dev/ttyAMA0")
    ser.write(b"test!")
    print(ser.read())


def main():
    serial_tests()


if __name__ == "__main__":
    main()
