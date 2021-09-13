'''
This file holds the class that controls the bigBear Orbital Shakers (Stickiness)
The port is specified by the specific application.

initParameters with a velocity and acceleration should be called before the shaker begins shaking
setVelocity can be used to change the initialized velocity
home attempts to home, but gives up after three attempts (often the shaker simply needs time if three errors occur)
startMotors shakes the plate at the specified acceleration and velocity
stopMotors slows down the shaker and attempts to home it
brake stops the shaker immediately
'''
import serial
import io,time

class OrbitalShaker:
    def __init__(self,port):
        self.port = port
        self.ser = serial.Serial(port=self.port,
                                        baudrate=9600,
                                        bytesize=serial.EIGHTBITS,
                                        parity=serial.PARITY_NONE,
                                        stopbits=serial.STOPBITS_TWO,
                                        timeout=0.1)
        self.controller = io.TextIOWrapper(io.BufferedRWPair(self.ser, self.ser, 1),
                                        newline = '\r',
                                        line_buffering = True)
    def _write(self,cmd):
        #Adds the carriage return
        self.controller.write(cmd+"\r")


    def initParameters(self, acceleration = 0,velocity = 452):
        if acceleration > 10 or acceleration < 0:
            print("Acceleration of %d out of bounds"%acceleration)
            acceleration = 0
        acc_cmd = "A" + str(int(acceleration))
        self._write(acc_cmd)
        if velocity < 60 or velocity > 3570:
            print("Velocity of %d out of bounds"%velocity)
            velocity = 452
        vel_cmd = "V" + str(int(velocity))
        self._write(vel_cmd)
        #Ensure hysteresis
        self._write("E")

    def home(self):
        self._write("Q")
        status = self.controller.readline()
        while status.strip() in ["RAMP+","RAMP-","RUN"]:
            self._write("Q")
            status = self.controller.readline()
            time.sleep(1)
        print("Shaker Status:",status)
        errors = 0
        while status.strip() != "STOP":
            self._write("B")
            time.sleep(1)
            self._write("F")
            time.sleep(1)
            while status.strip() in ["RAMP+","RAMP-","RUN"]:
                self._write("Q")
                status = self.controller.readline()
                time.sleep(1)
            if errors > 2:
                print("\tShaker Failed to Home")
                return False
            errors += 1
        return True


    def setVelocity(self,velocity = 552):
        if velocity < 60:
            velocity = 60
        elif velocity > 3570:
            velocity = 3570
        vel_cmd = "V" + str(int(velocity))
        self._write(vel_cmd)

    def startMotors(self):
        self._write("G")

    def stopMotors(self):
        self._write("S")

    def brake(self):
        self._write("B")

if __name__ == "__main__":

    shaker = OrbitalShaker("com4")
    shaker.initParameters()
    shaker.home()
    shaker.startMotors()
    time.sleep(5)
    shaker.stopMotors()
    time.sleep(5)
    shaker.home()

