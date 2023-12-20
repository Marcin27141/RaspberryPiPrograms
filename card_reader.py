#!/usr/bin/env python3
# pylint: disable=no-member

import time
import RPi.GPIO as GPIO
from config import *
from mfrc522 import MFRC522
import board
import neopixel

def start():
    MIFAREReader = MFRC522()
    lastCardId = 0
    lastRead = time.time()

    OK_CARD_ID = 507384896822

    while True:
        (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
        if status == MIFAREReader.MI_OK:
            (status, uid) = MIFAREReader.MFRC522_Anticoll()
            if status == MIFAREReader.MI_OK:
                num = 0
                for i in range(0, len(uid)):
                    num += uid[i] << (i*8)
                if time.time() - lastRead > 5 or num != lastCardId:
                    lastRead = time.time()
                    lastCardId = num
                    print(f"Card read UID: {num}, time: {time.time()}")
                    if num == OK_CARD_ID:
                        showLeds((0, 255, 0))
                        buzzerOk()
                        clearLeds()
                    else:
                        showLeds((255, 0, 0))
                        buzzerError()
                        clearLeds()
                        
def buzzer(state):
    GPIO.output(buzzerPin, not state)

def buzzerOk():
    buzzer(True)
    time.sleep(1)
    buzzer(False)

def buzzerError():
    buzzer(True)
    time.sleep(0.25)
    buzzer(False)
    time.sleep(0.25)
    buzzer(True)
    time.sleep(0.25)
    buzzer(False)
    time.sleep(0.25)
    buzzer(True)
    time.sleep(0.25)
    buzzer(False)

def getPixels():
    return neopixel.NeoPixel(board.D18, 8, brightness=1.0/32, auto_write=False)

def showLeds(color):
    pixels = getPixels()
    pixels.fill(color)
    pixels.show()

    
def clearLeds():
    pixels = getPixels()
    pixels.fill((0, 0, 0))
    pixels.show()

if __name__ == "__main__":
    clearLeds()
    start()
    GPIO.cleanup()