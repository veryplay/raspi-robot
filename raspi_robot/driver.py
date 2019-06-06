#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from pandas import Series
import Queue
from Queue import Empty
import signal
import time
from threading import Thread
import RPi.GPIO as GPIO

from decelerator import Decelerator
from lifecycle import LifeCycle
from ultrasonic import Ultrasonic
from vision import Vision

logger = logging.getLogger(__name__)

class Driver(LifeCycle):

    CACHE_LENGTH = 10

    DRIVER_LEFT_A = 5
    DRIVER_LEFT_B = 6
    DRIVER_RIGHT_A = 13
    DRIVER_RIGHT_B = 26

    def __init__(self):
        super(Driver, self).__init__()

    def do_start(self):
        self.queue = Queue.Queue(self.CACHE_LENGTH)
        self.cache = []

        self._bind_signal()
        
        self.init_gpio()

        self.decelerator = Decelerator()
        self.decelerator.start()

        self.ultrasonic = Ultrasonic(self)
        self.ultrasonic.start()

        self.vision = Vision()
        self.vision.start()

        self.cd_thread = Thread(name = "DriverThread", target = self.run)
        self.cd_thread.start()

        logger.info("start completely.")
    
    def do_stop(self):
        self._unbind_signal()
        
        if self.ultrasonic:
            self.ultrasonic.stop()

        while (hasattr(self, "cd_thread") 
            and self.cd_thread 
            and self.cd_thread.isAlive()):
            self.cd_thread.join(1)
            logger.warn("wait %s to finish.", self.cd_thread.getName())

        if self.decelerator:
            self.decelerator.stop()

        if self.vision:
            self.vision.stop()

        self.clean_gpio()

        self.queue.queue.clear()
        logger.info("stop completely.")

    def run(self):
        begin_time = int(time.time())
        while not self.should_stop():
            try:
                end_time = int(time.time())
                delta = end_time - begin_time
                if delta > 30:
                    self.vision.trigger_vision_event()
                    begin_time = end_time

                distance = self.queue.get(block = True, timeout = 0.01)

                cache_count = len(self.cache)
                if cache_count >= self.CACHE_LENGTH:
                    self.cache.pop(0)
                    self.cache.append(distance)

                else:
                    self.cache.append(distance)

                cache_describe = Series(self.cache).describe()
                mean = cache_describe["mean"]
                std = cache_describe["std"]
                if abs(distance - mean) > 2 * std:
                    logger.warn("distance is invalid.")
                    continue

                if distance > 70:
                    self.decelerator.change_decelerator_left(100)
                    self.decelerator.change_decelerator_right(100)
                    self.forward()
                    logger.info("distance %d cm, robot forward.", distance)
                
                elif distance > 30 and distance <= 70:
                    self.decelerator.change_decelerator_left(distance / 10 * 10)
                    self.decelerator.change_decelerator_right(distance / 10 * 10 - 10)
                    self.turn_right()
                    logger.info("distance %d cm, robot turn right.", distance)

                elif distance > 20 and distance <= 30:
                    self.decelerator.change_decelerator_left(distance / 10 * 10 - 10)
                    self.decelerator.change_decelerator_right(distance / 10 * 10)
                    self.turn_left()
                    logger.info("distance %d cm, robot turn left.", distance)

                elif distance > 5 and distance <= 20:
                    self.decelerator.change_decelerator_left(40)
                    self.decelerator.change_decelerator_right(40)
                    self.backup()
                    logger.info("distance %d cm, robot backup.", distance)

                else :
                    self.decelerator.change_decelerator_left(0)
                    self.decelerator.change_decelerator_right(0)
                    self.braking()
                    logger.info("distance %d cm, robot braking.", distance)
                
            except Queue.Empty:
                continue
            except Exception:
                logger.error("DriverThread run failed.", exc_info=1)

    def get_queue(self):
        return self.queue

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
