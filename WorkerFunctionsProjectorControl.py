
import time,datetime
import numpy as np
import time
import mmap
import cv2
import os
import fcntl
import struct


DEFAULT_SLAVE_ADDRESS = 0x36
DEFAULT_I2C_BUS = 1


class i2c():
    busnum = 0
    slave_address = 0
    fd = None
    I2C_TENBIT = 0x0704
    I2C_SLAVE = 0x0703


    def __init__(self,busnum,slave_address):        
        
        self.busnum = busnum
        self.slave_address = slave_address
        self.fd = os.open('/dev/i2c-%d' % self.busnum, os.O_RDWR)

        fcntl.ioctl(self.fd, self.I2C_TENBIT, 0)
        fcntl.ioctl(self.fd, self.I2C_SLAVE, self.slave_address >> 1)

    def write(self, data):
        if self.fd > 0:
            os.write(self.fd, bytearray(data))

    def read(self, numbytes):
        if self.fd > 0:
            retval = list(bytearray(os.read(self.fd, numbytes)))
            return retval
        


class Projector():

    i2c_ = None


    def __init__(self, projector_dimension=(360,640), delayBetweenCommand=0.1,LedCurrent = 500):
        
        self.projector_dimension =  [projector_dimension[0],projector_dimension[1],4]
        self.delayBetweenCommand = delayBetweenCommand  #0.1 is usually ok
        self.LedCurrent = LedCurrent #between 0 - 1000
        
        self.i2c_ = i2c(DEFAULT_I2C_BUS, DEFAULT_SLAVE_ADDRESS)
        
        #disable dithering
        payload = [0x7e]
        value = 0x02
        payload.extend(list(bytearray(struct.pack(">I", value))))
        self.i2c_.write(payload)
        #disable auto gain
        payload = [0x50]
        value = 0x06
        payload.extend(list(bytearray(struct.pack(">I", value))))
        self.i2c_.write(payload)
        #disable color coordinate adjustment (CCA) function
        payload = [0x5e]
        value = 0x00
        payload.extend(list(bytearray(struct.pack(">I", value))))
        self.i2c_.write(payload)        
        #disable WPC
        payload = [0xB5]
        value = 0x00
        payload.extend(list(bytearray(struct.pack(">I", value))))
        self.i2c_.write(payload)

        #map dlp image buffer to np array
        #COLOR_BGR2BGR565
        c=2
        self.vfileBuffer =  open('/dev/fb0', 'r+b')        
        self.mappedBuffer = np.memmap('/dev/fb0', dtype=np.uint8, mode='w+', shape=(self.projector_dimension[0],self.projector_dimension[1],c)) 
        self.driveCurrentOn(self.LedCurrent)
        
        self.unfreeze()


    
    
    #command to dlp
    def writeLedCurrentRed(self,val):
        payload = [0x12]
        payload.extend(list(bytearray(struct.pack(">I", val & 0x7ff))))
        self.i2c_.write(payload)

    def writeLedCurrentGreen(self,val):
        payload = [0x13]
        payload.extend(list(bytearray(struct.pack(">I", val & 0x7ff))))
        self.i2c_.write(payload)
    def writeLedCurrentBlue(self,val):
        payload = [0x14]
        payload.extend(list(bytearray(struct.pack(">I", val & 0x7ff))))
        self.i2c_.write(payload)

    def writeLedEnable(self,enableR,enableG,enableB):
        payload = [0x16]
        value = 0
        value |= (enableR & 0x1) << 0
        value |= (enableG & 0x1) << 1
        value |= (enableB & 0x1) << 2
        payload.extend(list(bytearray(struct.pack(">I", value))))
        self.i2c_.write(payload)

    def propagateLedCurrent(self,val):
        payload = [0x39]
        payload.extend(list(bytearray(struct.pack(">I", val))))
        self.i2c_.write(payload)
        self.i2c_.write([0x3A, 0x00, 0x00, 0x00, 0x01])
        self.i2c_.write([0x38, 0x00, 0x00, 0x00, 0xD3])

    def freeze(self):
        time.sleep(self.delayBetweenCommand)
        payload = [0xa3]
        value = 0x01
        payload.extend(list(bytearray(struct.pack(">I", value))))
        self.i2c_.write(payload)
        time.sleep(0.05)        

    def unfreeze(self):
        time.sleep(self.delayBetweenCommand)
        payload = [0xa3]
        value = 0x00
        payload.extend(list(bytearray(struct.pack(">I", value))))
        self.i2c_.write(payload)
        time.sleep(0.05)

    def driveCurrentOn(self,ledCurrent=500):        
        
        time.sleep(self.delayBetweenCommand)
        self.writeLedEnable(0,0,0)
        time.sleep(self.delayBetweenCommand)
        self.propagateLedCurrent(1)
        time.sleep(self.delayBetweenCommand)
        self.writeLedCurrentRed(ledCurrent)
        time.sleep(self.delayBetweenCommand)
        self.writeLedCurrentGreen(ledCurrent)
        time.sleep(self.delayBetweenCommand)
        self.writeLedCurrentBlue(ledCurrent)
        time.sleep(self.delayBetweenCommand)
        self.propagateLedCurrent(1)
        time.sleep(self.delayBetweenCommand)
        self.writeLedEnable(1,1,1)

    def driveCurrentOff(self):
        time.sleep(self.delayBetweenCommand)
        self.writeLedEnable(0,0,0)
    


    #image projection related
    def clear():
        imgGeneric = np.zeros(self.projector_dimension,np.uint8)
        self.showImage(imgGeneric)
        
        
    def showImage(self,img):        
        #convert to 565
        
        
        #img_ = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR565 )
        #img_ = cv2.cvtColor(img, cv2.COLOR_RGB2BGR565 )
        

        #self.freeze()
        #time.sleep(self.delayBetweenCommand)
        self.mappedBuffer[:] = img
        #self.unfreeze()        
        #time.sleep(self.delayBetweenCommand*2)
        #self.freeze()    

    def showTarget(self):
        
        imgGeneric = np.zeros(self.projector_dimension[0:2],np.uint8)
        imgGeneric[:,320]=255
        imgGeneric[180,:]=255
        imgGeneric[0,:]=255
        imgGeneric[359,:]=255
        imgGeneric[:,0]=255
        imgGeneric[:,639]=255
        self.showImage(imgGeneric)




    
