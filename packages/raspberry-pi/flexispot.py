import serial
from gpiozero import LED
from time import sleep
import sys

SERIAL_PORT = "/dev/ttyAMA0" # GPIO14 (TX) and GPIO15 (RX)
PIN_20 = 18

SUPPORTED_COMMANDS = {
    "up":       bytearray(b'\x9b\x06\x02\x01\x00\xfc\xa0\x9d'),
    "down":     bytearray(b'\x9b\x06\x02\x02\x00\x0c\xa0\x9d'),
    "m":        bytearray(b'\x9b\x06\x02\x20\x00\xac\xb8\x9d'),
    "wake_up":  bytearray(b'\x9b\x06\x02\x00\x00\x6c\xa1\x9d'),
    "preset_1": bytearray(b'\x9b\x06\x02\x04\x00\xac\xa3\x9d'),
    "preset_2": bytearray(b'\x9b\x06\x02\x08\x00\xac\xa6\x9d'),
    "preset_3": bytearray(b'\x9b\x06\x02\x10\x00\xac\xac\x9d'),
    "preset_4": bytearray(b'\x9b\x06\x02\x00\x01\xac\x60\x9d'),
}

class LoctekMotion():

    def __init__(self, serial, pin_20):
        """Initialize LoctekMotion"""
        self.serial = serial

        led = LED(pin_20)
        print("pin 20 state: {}".format(led.value))
        led.on()
        print("pin 20 state: {} -- sleeping".format(led.value))
        sleep(1)
        print("pin 20 state: {}".format(led.value))

    def execute_command(self, command_name: str):
        """Execute command"""
        command = SUPPORTED_COMMANDS.get(command_name)

        if not command:
            raise Exception("Command not found")

        self.serial.write(command)

    def print_seven_segment(self, value):
        a = '*' if value[-1] == '1' else ' '
        b = '*' if value[-2] == '1' else ' '
        c = '*' if value[-3] == '1' else ' '
        d = '*' if value[-4] == '1' else ' '
        e = '*' if value[-5] == '1' else ' '
        f = '*' if value[-6] == '1' else ' '
        g = '*' if value[-7] == '1' else ' '
        h = '.' if value[-8] == '1' else ' '

        print(" {}{}{} ".format(a, a, a))
        print("{}   {}".format(f, b))
        print("{}   {}".format(f, b))
        print("{}   {}".format(f, b))
        print(" {}{}{} ".format(g, g, g))
        print("{}   {}".format(e, c))
        print("{}   {}".format(e, c))
        print("{}   {}".format(e, c))
        print(" {}{}{} {}".format(d, d, d, h))

    def decode_seven_segment(self, byte):
        binaryByte = bin(byte).replace("0b","").zfill(8)
        self.print_seven_segment(binaryByte)
        decimal = False
        if binaryByte[0] == "1":
            decimal = True
        if binaryByte[1:] == "0111111":
            return 0, decimal
        if binaryByte[1:] == "0000110":
            return 1, decimal
        if binaryByte[1:] == "1011011":
            return 2, decimal
        if binaryByte[1:] == "1001111":
            return 3, decimal
        if binaryByte[1:] == "1100110":
            return 4, decimal
        if binaryByte[1:] == "1101101":
            return 5, decimal
        if binaryByte[1:] == "1111101":
            return 6, decimal
        if binaryByte[1:] == "0000111":
            return 7, decimal
        if binaryByte[1:] == "1111111":
            return 8, decimal
        if binaryByte[1:] == "1101111":
            return 9, decimal
        if binaryByte[1:] == "1000000":
            return 10, decimal
        return -1, decimal

    def current_height(self):
        while True:
            try:
                start = self.serial.read(1)[0]
                if start != 0x9b:
                    raise Exception("Unexpected start: {}".format(start))
                
                length = self.serial.read(1)[0]
                if length == 0:
                    continue
                
                data = self.serial.read(length)
                if data[-1] != 0x9d:
                    raise Exception("Unexpected end: {}".format(data[-1]))

                print("Received message: {}".format(data))

                if length == 7:
                    height1, decimal1 = self.decode_seven_segment(data[1])
                    height1 = height1 * 100
                    height2, decimal2 = self.decode_seven_segment(data[2])
                    height2 = height2 * 10
                    height3, decimal3 = self.decode_seven_segment(data[3])
                    if height1 < 0 or height2 < 0 or height3 < 0:
                        print("Display Empty")
                    else:
                        finalHeight = height1 + height2 + height3
                        decimal = decimal1 or decimal2 or decimal3
                        if decimal == True:
                            finalHeight = finalHeight/10
                        print("Height: ", finalHeight)
            except Exception as e:
                print(e)
                break

def main():
    try:
        command = sys.argv[1]
        ser = serial.Serial(SERIAL_PORT, 9600, timeout=500)
        locktek = LoctekMotion(ser, PIN_20)
        while True:
            print("will execute command")
            locktek.execute_command(command)
        print("will get height")
        locktek.current_height()
        print("done?")
    # Error handling for serial port
    except serial.SerialException as e:
        print(e)
        return
    # Error handling for command line arguments
    except IndexError:
        program = sys.argv[0]
        print("Usage: python3",program,"[COMMAND]")
        print("Supported Commands:")
        for command in SUPPORTED_COMMANDS:
            print("\t", command)
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(1)

if __name__ == "__main__":
    main()
