'''
This file holds the class that communicates with the TC36 Temperature Controller

Many of the serial commands have been separated into their own functions
however the sendCommand function allows for the direct input of commands
See the documentation for details about which additional commands can be sent.

'''
import serial
import io,time

class TempController:
    def __init__(self,port):
        self.port = port
        self.ser = serial.Serial(port=self.port,
                                        baudrate=9600,
                                        bytesize=serial.EIGHTBITS,
                                        parity=serial.PARITY_NONE,
                                        stopbits=serial.STOPBITS_ONE,
                                        timeout=0.05)
        self.controller = io.TextIOWrapper(io.BufferedRWPair(self.ser, self.ser, 1),
                                        newline = '\r',
                                        line_buffering = True)

    def sendCommand(self,command,value = 0):
        max_val = 16**8
        max_positive = max_val//2-1;
        assert(value < max_val)
        val_h = hex(int(value))[2:] #removes the 0x
        while len(val_h) < 8:
            if value < 0:
                val_h = "f"+val_h
            else:
                val_h = "0"+val_h
        cmd = "00"+command+val_h
        #compute checksum
        sum_d = 0
        for char in cmd:
            sum_d += ord(char)
        sum_h = hex(sum_d)[-2:]
        cmd = "*"+cmd+sum_h+"\r"
        self.controller.write(cmd)
        ret = self.controller.read(12)
        if "X" not in ret:
            ret_val = int(ret[1:9],16)
            if ret_val > max_positive:
                ret_val -= max_val
            return ret_val
        else:
            #ncorrect checksum
            return ret

    def readTemperature(self):
        return self.sendCommand("01")/100

    def setTemperature(self,temp):
        if abs(temp) > 511:
            print("Temperature of %3.1f is out of range"%temp)
            exit(1)
        ret = self.sendCommand("1c",int(temp*100))
        if type(ret) == int:
            if ret/100 == temp:
                return ret/100
        print("Failed to set temperature to %3.1f"%temp)
        exit(1)

    def readControlTemp(self):
        #The temperature the peltier is trying to maintain
        return self.sendCommand("03")/100

    def readPowerOut(self):
        #The percentage of its cooling/heating ability being used
        return self.sendCommand("02")/511*100

    def readControlType(self):
        #The control method (usually PID)
        control = ["Deadband","PID","Computer"]
        return control[self.sendCommand("44")]

    def checkAlarms(self):
        #Which alarms are triggered
        isAlarm = self.sendCommand("05")
        detected_alarms = []
        if isAlarm:
            alarms = ["HIGH","LOW","COMPUTER CONTROLLED","OVER CURRENT","OPEN INPUT1","OPEN INPUT2","DRIVER LOW INPUT VOLTAGE"]
            flags = bin(isAlarm)[2:]
            for i,flag in enumerate(flags):
                if int(flag):
                    detected_alarms.append(alarms[i])

        return detected_alarms

    def readTempBandwidth(self):
        #The range around the desired temperature that is permitted
        return self.sendCommand("51")/100

    def setTempBandwidth(self,val):
        #The range around the desired temperature that is permitted
        return self.sendCommand("1d",int(val*100))

    def toggleOn(self,on):
        #This does not seem to be operational...
        assert (on in [1,0])
        self.sendCommand("2d",on)




if __name__ == "__main__":
    controller = TempController("COM3")
    print("Temperature:",controller.readTemperature())
    controller.setTemperature(53)
    time.sleep(40)
    print("Temperature:",controller.readTemperature())
    controller.setTemperature(43)
    time.sleep(40)
    print("Temperature:",controller.readControlType())
    print("Bandwidth:",controller.readTempBandwidth())
