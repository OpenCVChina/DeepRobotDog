import socket
import struct
import threading
import time


class Controller:
    def __init__(self, dst):
        self.lock = False
        self.last_ges = "stop"
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.dst = dst

    # used to send a pack to robot dog
    def send(self, pack):
        self.socket.sendto(pack, self.dst)

    def drive_dog(self, ges, val = 10000):
        print(ges)
        if self.lock or ges == self.last_ges:
            return

        if self.last_ges == "squat" and ges != "squat":
            # stand up
            self.send(struct.pack('<3i', 0x21010202, 0, 0))
        else:
            # stop all actions
            self.send(struct.pack('<3i', 0x21010130, 0, 0))
            self.send(struct.pack('<3i', 0x21010131, 0, 0))
            self.send(struct.pack('<3i', 0x21010102, 0, 0))
            self.send(struct.pack('<3i', 0x21010135, 0, 0))

        if self.last_ges != "squat" and ges == "squat":
            self.send(struct.pack('<3i', 0x21010202, 0, 0))
        elif ges == "turning":
            def turn_360():
                self.lock = True
                self.send(struct.pack('<3i', 0x21010135, 13000, 0))
                time.sleep(2.84)  # need time to turn 360 degrees
                self.send(struct.pack('<3i', 0x21010135, 0, 0))
                self.lock = False

            turn_thread = threading.Thread(target=turn_360)
            turn_thread.start()
        elif ges == "twisting":
            def dance():
                self.lock = True
                self.send(struct.pack('<3i', 0x21010204, 0, 0))
                time.sleep(22)  # dance 22 seconds then it can process next gesture
                self.lock = False

            twist_thread = threading.Thread(target=dance)
            twist_thread.start()
        elif ges == "forward":
            self.send(struct.pack('<3i', 0x21010130, val, 0))
        elif ges == "back":
            self.send(struct.pack('<3i', 0x21010130, -val, 0))
        elif ges == "right":
            self.send(struct.pack('<3i', 0x21010131, val, 0))
        elif ges == "left":
            self.send(struct.pack('<3i', 0x21010131, -val, 0))

        self.last_ges = ges
