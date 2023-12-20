#!/usr/bin/env python3
# This program must be executed with root privileges.
# Enter the command:
# sudo ./ws2812.py
import time
import os
import board
import neopixel
from config import *
import w1thermsensor
import busio
import adafruit_bme280.advanced as adafruit_bme280

NUMBER_OF_LEDS = 8

def ds18b20():
    sensor = w1thermsensor.W1ThermSensor()
    return sensor.get_temperature()

def setUpButtons():
    GPIO.add_event_detect(buttonRed, GPIO.FALLING, callback=redButtonPressedCallback, bouncetime=200)
    GPIO.add_event_detect(buttonGreen, GPIO.FALLING, callback=greenButtonPressedCallback, bouncetime=200)
    
def redButtonPressedCallback(channel):
    showDs18B20Reading()

def greenButtonPressedCallback(channel):
    bme280 = initBme280()
    temp, humidity, pressure = readBme280(bme280)
    showTemp(temp)
    startCheckingEncoder(bme280)    

def getPixels():
    return neopixel.NeoPixel(board.D18, 8, brightness=1.0/32, auto_write=False)

def getUpperLedToLight(lowest, highest, read):
    normalized = max(read - lowest, 0)
    step = (highest - lowest) / NUMBER_OF_LEDS
    return int(normalized / step) + 1

def showTemp(temp):
    color = (0, 0, 255) if temp < 23 else ((0, 255, 0) if temp < 25 else (255, 0, 0))
    pixels = getPixels()
    for i in range(getUpperLedToLight(21, 28, temp)):
        pixels[i] = color
    pixels.show()

def showBmeHumidity(humidity):
    color = (0, 0, 255) if humidity > 50 else (255, 0, 0)
    pixels = getPixels()
    for i in range(getUpperLedToLight(0, 100, humidity)):
        pixels[i] = color
    pixels.show()

def showBmePressure(pressure):
    color = (0, 0, 255) if pressure < 1000 else (0, 255, 0)
    pixels = getPixels()
    for i in range(getUpperLedToLight(950, 1050, pressure)):
        pixels[i] = color
    pixels.show()

def startCheckingEncoder(bme280):
    currentMeasure = 0

    encoderRightPrevoiusState = GPIO.input(encoderRight)
    last_turn_time = -1
    
    while (last_turn_time != -1 and time.time() - last_turn_time > 5):
        encoderRightCurrentState = GPIO.input(encoderRight)

        if(encoderRightPrevoiusState == 1 and encoderRightCurrentState == 0):
            temp, humidity, pressure = readBme280(bme280)
            
            if currentMeasure == 0:
                showTemp(temp)
            elif currentMeasure == 1:
                showBmePressure(pressure)
            else:
                showBmeHumidity(humidity)
            currentMeasure = (currentMeasure + 1) % 3
            last_turn_time = time.time()

        encoderRightPrevoiusState = encoderRightCurrentState

    showDs18B20Reading()

def initBme280():
    i2c = busio.I2C(board.SCL, board.SDA)
    bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, 0x76)

    bme280.sea_level_pressure = 1013.25
    bme280.standby_period = adafruit_bme280.STANDBY_TC_500
    bme280.iir_filter = adafruit_bme280.IIR_FILTER_X16
    bme280.overscan_pressure = adafruit_bme280.OVERSCAN_X16
    bme280.overscan_humidity = adafruit_bme280.OVERSCAN_X1
    bme280.overscan_temperature = adafruit_bme280.OVERSCAN_X2
    return bme280

def readBme280(bme280):
    bmeTemp = bme280.temperature
    bmeHumidity = bme280.humidity
    bmePressure = bme280.pressure
    return bmeTemp, bmeHumidity, bmePressure

def showDs18B20Reading() {
    dsTemp = ds18b20()
    showTemp(dsTemp)
}

if __name__ == "__main__":
    setUpButtons()
    showDs18B20Reading()
    while True:
        pass
