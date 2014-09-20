#!/usr/bin/python
import servos
import serial
import cwiid
import time
import logging
logging.basicConfig(level=logging.DEBUG)

class Wiimote(object):
    """docstring for Wiimote"""
    def __init__(self, servos):
        super(Wiimote, self).__init__()
        self.servos = servos
        # self.motion = None
        self.button_delay = 0.1
        self.servo_step = 0.1

    def pair(self):
        print("press 1 and 2 buttons")
        wii = None
        while (wii == None):
            try:
                wii = cwiid.Wiimote()
            except RuntimeError:
                print("Error connecting to the wiimote, press 1 and 2")
            else:
                print("Wiimote now connected")
                # wii.enable(cwiid.FLAG_MOTIONPLUS)
                wii.rpt_mode = cwiid.RPT_BTN | cwiid.RPT_NUNCHUK# | cwiid.RPT_MOTIONPLUS
                wii.led = 6
                return wii

    def run(self):
        s = self.servos
        button_delay = self.button_delay
        step = self.servo_step
        wii = self.pair()
        time.sleep(1) # let the buttons get set
        while True:
            buttons = wii.state["buttons"]
            # disconnect on home button
            if (buttons - cwiid.BTN_HOME == 0):
                print("closing")
                wii.rumble = 1
                time.sleep(1)
                wii.rumble = 0
                exit(wii)

            if "nunchuk" in wii.state:
                turn = wii.state["nunchuk"]["stick"][0]
                thrust = wii.state["nunchuk"]["stick"][1]

                if (thrust / 10 > 14):
                    print("faster")
                    s.thrust += step
                    time.sleep(button_delay)
                if (thrust / 10 < 12):
                    print("slower")
                    s.thrust -= step
                    time.sleep(button_delay)

                if (turn / 10 > 13):
                    print("turn right")
                    s.turn += (step * 2)
                    time.sleep(button_delay)

                if (turn / 10 < 13):
                    print("turn left")
                    s.turn -= (step * 2)
                    time.sleep(button_delay)

            if (buttons & cwiid.BTN_UP):
                print("y up")
                s.y += step
                time.sleep(button_delay)

            if (buttons & cwiid.BTN_DOWN):
                print("y down")
                s.y -= step
                time.sleep(button_delay)

            if (buttons & cwiid.BTN_LEFT):
                print("x left")
                s.x -= step
                time.sleep(button_delay)

            if (buttons & cwiid.BTN_RIGHT):
                print("x right")
                s.x += step
                time.sleep(button_delay)

            if (buttons & cwiid.BTN_B):
                print("toggle led")
                s.led = 1.0 - s.led
                time.sleep(button_delay)

            if (buttons & cwiid.BTN_MINUS):
                print("duct slower")
                s.duct -= step
                time.sleep(button_delay)

            if (buttons & cwiid.BTN_PLUS):
                print("duct faster")
                s.duct += step
                time.sleep(button_delay)

            # if "motionplus" in wii.state and s.led >= 0.5:
            #     if self.motion != wii.state["motionplus"]:
            #         print(wii.state["motionplus"])
            #         self.motion = wii.state["motionplus"]

            # print wii.state
            # time.sleep(1)

def main():
    try:
        s = servos.Servos(serial.Serial('/dev/ttyACM0', 9600))
        print("mounted ttyACM0")
    except SerialException:
        s = servos.Servos(serial.Serial('/dev/ttyACM1', 9600))
        print("mounted ttyACM1")

    wii = Wiimote(s)
    wii.run()

if __name__ == "__main__":
    main()