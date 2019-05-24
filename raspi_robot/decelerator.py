#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

import RPi.GPIO as GPIO

from lifecycle import LifeCycle

logger = logging.getLogger(__name__)

class Decelerator(LifeCycle):

    DECELERATOR_LEFT = 17
    DECELERATOR_RIGHT = 18

    def __init__(self):
        super(Decelerator, self).__init__()

    def do_start(self):
        self.init_gpio()

        self.pwm_left = GPIO.PWM(self.DECELERATOR_LEFT, 100)
        self.pwm_left.start(0)
        
        self.pwm_right = GPIO.PWM(self.DECELERATOR_RIGHT, 100)	
        self.pwm_right.start(0)

        logger.info("start completely.")

    def do_stop(self):
        if (hasattr(self, "pwm_left")
            and self.pwm_left):
            self.pwm_left.stop()
        
        if (hasattr(self, "pwm_right")
            and self.pwm_right):
            self.pwm_right.stop()

        self.clean_gpio()

        logger.info("stop completely.")
    
    def change_decelerator_left(self, duty_cycle):
        self.pwm_left.ChangeDutyCycle(duty_cycle)
    
    def change_decelerator_right(self, duty_cycle):
        self.pwm_right.ChangeDutyCycle(duty_cycle)

    @classmethod
    def init_gpio(cls):
        GPIO.setup([cls.DECELERATOR_LEFT, cls.DECELERATOR_RIGHT], GPIO.OUT)

    @classmethod
    def clean_gpio(cls):
        GPIO.cleanup([cls.DECELERATOR_LEFT, cls.DECELERATOR_RIGHT])
