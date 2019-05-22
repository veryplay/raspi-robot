#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import time
import sys

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    import fake_rpi
    sys.modules['RPi'] = fake_rpi.RPi
    import RPi.GPIO as GPIO

from lifecycle import LifeCycle

logger = logging.getLogger(__name__)

class Ultrasonic(LifeCycle):

    TRIG = 25
    ECHO = 12

    ACOUSTIC_WAVE_VELOCITY = 343

    def __init__(self):
        super(Ultrasonic, self).__init__()

    def do_start(self):
        self.init_gpio()
        logger.info("start completely.")

    def do_stop(self):
        self.clean_gpio()
        logger.info("stop completely.")

    def get_distance(self):
        GPIO.output(self.TRIG, True)
        time.sleep(0.00001)
        GPIO.output(self.TRIG, False)

        # 等待低电平结束,然后记录时间
        while not GPIO.input(self.ECHO):
            pass
        pulse_start = time.time()

        # 等待高电平结束, 然后记录时间
        while GPIO.input(self.ECHO):
            pass
        pulse_end = time.time()

        return int((pulse_end - pulse_start) * self.ACOUSTIC_WAVE_VELOCITY / 2 * 100)

    @classmethod
    def init_gpio(cls):
        GPIO.setup(TRIG, GPIO.OUT, initial = GPIO.LOW)
        GPIO.setup(ECHO, GPIO.IN)
    
    @classmethod
    def clean_gpio(cls):
        GPIO.cleanup([cls.TRIG, cls.ECHO])