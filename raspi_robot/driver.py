#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import signal
import time
from threading import Thread
import sys

import RPi.GPIO as GPIO

from decelerator import Decelerator
from lifecycle import LifeCycle
from ultrasonic import Ultrasonic

logger = logging.getLogger(__name__)

class Driver(LifeCycle):

    DRIVER_LEFT_A = 5
    DRIVER_LEFT_B = 6
    DRIVER_RIGHT_A = 13
    DRIVER_RIGHT_B = 19

    def __init__(self):
        super(Driver, self).__init__()

    def do_start(self):
        self._bind_signal()
        
        self.init_gpio()

        self.decelerator = Decelerator()
        self.decelerator.start()

        self.ultrasonic = Ultrasonic()
        self.ultrasonic.start()

        self.cd_thread = Thread(name = "DriverThread", target = self.run)
        self.cd_thread.start()

        logger.info("start completely.")
    
    def do_stop(self):
        self._unbind_signal()

        if (hasattr(self, "cd_thread") 
            and self.cd_thread 
            and self.cd_thread.isAlive()):
            self.cd_thread.join(2)

        if self.decelerator:
            self.decelerator.stop()

        if self.ultrasonic:
            self.ultrasonic.stop()

        self.clean_gpio()

        logger.info("stop completely.")

    def run(self):
        while not self.should_stop():
            distance = self.ultrasonic.get_distance()
            if distance > 50:
                self.decelerator.change_decelerator_left(100)
                self.decelerator.change_decelerator_right(100)
                self.forward()
                logger.info("distance %d cm, robot forward.", distance)
            
            elif distance >40 and distance < 50:
                self.decelerator.change_decelerator_left(distance / 10 * 10)
                self.decelerator.change_decelerator_right(distance / 10 * 10)
                logger.info("distance %d cm, robot decelerator.", distance)
            
            elif distance > 30 and distance < 40:
                self.decelerator.change_decelerator_left(distance / 10 * 10 + 20)
                self.decelerator.change_decelerator_right(distance / 10 * 10)
                self.turn_right()
                logger.info("distance %d cm, robot turn right.", distance)

            elif distance > 20 and distance < 30:
                self.decelerator.change_decelerator_left(distance / 10 * 10)
                self.decelerator.change_decelerator_right(distance / 10 * 10 + 20)
                self.turn_left()
                logger.info("distance %d cm, robot turn left.", distance)

            elif distance > 10 and distance < 20:
                self.decelerator.change_decelerator_left(20)
                self.decelerator.change_decelerator_right(20)
                self.backup()
                logger.info("distance %d cm, robot backup.", distance)

            else :
                self.decelerator.change_decelerator_left(0)
                self.decelerator.change_decelerator_right(0)
                self.braking()
                logger.info("distance %d cm, robot braking.", distance)

            time.sleep(0.2)

    @classmethod
    def init_gpio(cls):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup([cls.DRIVER_LEFT_A, cls.DRIVER_LEFT_B, cls.DRIVER_RIGHT_A, cls.DRIVER_RIGHT_B], GPIO.OUT)

    @classmethod
    def clean_gpio(cls):
        GPIO.cleanup([cls.DRIVER_LEFT_A, cls.DRIVER_LEFT_B, cls.DRIVER_RIGHT_A, cls.DRIVER_RIGHT_B])

    @classmethod
    def forward(cls):
        GPIO.output(cls.DRIVER_LEFT_A,  GPIO.HIGH)
        GPIO.output(cls.DRIVER_LEFT_B,  GPIO.LOW)
        GPIO.output(cls.DRIVER_RIGHT_A,  GPIO.HIGH)
        GPIO.output(cls.DRIVER_RIGHT_B,  GPIO.LOW)

    @classmethod
    def backup(cls):
        GPIO.output(cls.DRIVER_LEFT_A, GPIO.LOW)
        GPIO.output(cls.DRIVER_LEFT_B, GPIO.HIGH)
        GPIO.output(cls.DRIVER_RIGHT_A, GPIO.LOW)
        GPIO.output(cls.DRIVER_RIGHT_B, GPIO.HIGH)

    @classmethod
    def turn_left(cls):
        GPIO.output(cls.DRIVER_LEFT_A, GPIO.HIGH)
        GPIO.output(cls.DRIVER_LEFT_B, GPIO.LOW)
        GPIO.output(cls.DRIVER_RIGHT_A, GPIO.LOW)
        GPIO.output(cls.DRIVER_RIGHT_B, GPIO.HIGH)
    
    @classmethod
    def turn_right(cls):
        GPIO.output(cls.DRIVER_LEFT_A, GPIO.LOW)
        GPIO.output(cls.DRIVER_LEFT_B, GPIO.HIGH)
        GPIO.output(cls.DRIVER_RIGHT_A, GPIO.HIGH)
        GPIO.output(cls.DRIVER_RIGHT_B, GPIO.LOW)

    @classmethod
    def braking(cls):
        GPIO.output(cls.DRIVER_LEFT_A, False)
        GPIO.output(cls.DRIVER_LEFT_B, False)
        GPIO.output(cls.DRIVER_RIGHT_A, False)
        GPIO.output(cls.DRIVER_RIGHT_B, False)

    def _bind_signal(self):
        # bind signal
        self.hold_sigint = signal.signal(signal.SIGINT, self._handler_signal)
        self.hold_sigterm = signal.signal(signal.SIGTERM, self._handler_signal)

    def _unbind_signal(self):
        # unbind signal
        signal.signal(signal.SIGINT, self.hold_sigint)
        signal.signal(signal.SIGTERM, self.hold_sigterm)

    def _handler_signal(self, signum, frame):
        logger.info("receive a kill signal %s=%s.", signum, frame)
        self.stop()
