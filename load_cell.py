# -*- coding: utf-8 -*-
# @Author: cbott
# @Date:   2018-07-01 23:40:22
# @Last Modified by:   cbott
# @Last Modified time: 2018-07-02 23:16:02

"""
This library is designed to facilitate reading from the Sparkfun
load cell amplifier (https://sparkfun.com/products/13879)
on a Raspberry Pi running python 3

The code is heavily based off of these works:
https://github.com/tatobari/hx711py/blob/master/hx711.py
https://github.com/bogde/HX711/blob/master/HX711.cpp
"""

import time

import RPi.GPIO as GPIO


def bits_to_int(bit_list):
    """
    Convert a list of True/False to decimal, interpreting the list as binary MSB first
    Essentially np.packbits()
    """
    bit_string = ''
    for bit in bit_list:
        if bit:
            bit_string += '1'
        else:
            bit_string += '0'
    return int(bit_string, 2)


class HX711:
    def __init__(self, datapin, clockpin):
        GPIO.setmode(GPIO.BOARD)
        self.datapin = datapin
        self.clockpin = clockpin
        self.gain = 1  # TODO: allow user to set this

        GPIO.setup(self.datapin, GPIO.IN)
        GPIO.setup(self.clockpin, GPIO.OUT)

    def is_ready(self):
        return GPIO.input(self.datapin) == GPIO.LOW

    def read(self):
        while not self.is_ready():
            pass

        dataBits = [[False] * 8 for i in range(3)]
        dataBytes = [0x0] * 4

        # Read in 24 bits of data
        for j in range(2, -1, -1):
            for i in range(0, 8, 1):
                GPIO.output(self.clockpin, True)
                dataBits[j][i] = GPIO.input(self.datapin)
                GPIO.output(self.clockpin, False)
            dataBytes[j] = bits_to_int(dataBits[j])

        # Set channel and gain factor for next reading
        # Between 1 and 3 additional clock pulses are required here
        for i in range(self.gain):
            GPIO.output(self.clockpin, True)
            GPIO.output(self.clockpin, False)

        # TODO: Figure out why this is a thing
        if dataBytes[2] & 0x80:
            filler = 0xFF
        else:
            filler = 0x00

        return (filler << 24) | (dataBytes[2] << 16) | (dataBytes[1] << 8) | (dataBytes[0])

    def power_down(self):
        GPIO.output(self.clockpin, False)
        GPIO.output(self.clockpin, True)
        time.sleep(0.0001)

    def power_up(self):
        GPIO.output(self.clockpin, False)
        time.sleep(0.0001)

    def reset(self):
        self.power_down()
        self.power_up()


if __name__ == '__main__':
    loadcell = HX711(38, 40)
    try:
        while 1:
            print(loadcell.read())
            time.sleep(1)
    finally:
        GPIO.cleanup()
