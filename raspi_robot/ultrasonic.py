#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import Queue
import time
import sys
import RPi.GPIO as GPIO
from threading import Thread

from lifecycle import LifeCycle

logger = logging.getLogger(__name__)

class Ultrasonic(LifeCycle):

    TRIG = 23
    ECHO = 24

    ACOUSTIC_WAVE_VELOCITY = 343

    def __init__(self, driver):
        super(Ultrasonic, self).__init__()
        self.driver = driver
        self.queue = self.driver.get_queue()

    def do_start(self):
        self.init_gpio()

        self.us_thread = Thread(name = "UltrasonicThread", target = self.run)
        self.us_thread.start()

        logger.info("start completely.")

    def do_stop(self):
        while (hasattr(self, "us_thread") 
            and self.us_thread 
            and self.us_thread.isAlive()):
            self.us_thread.join(1)
            logger.warn("wait %s to finish.", self.us_thread.getName())

        self.clean_gpio()
        logger.info("stop completely.")

    def run(self):
        while not self.should_stop():
            try:
                distance = self.get_distance()
                self.queue.put_nowait(distance)
            except Queue.Full:
                logger.warn("Distance Queue is full, wait Driver to consume it.")
            except Exception:
                logger.error("UltrasonicThread run failed.", exc_info=1)
            finally:
                time.sleep(0.2)

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
        GPIO.setup(cls.TRIG, GPIO.OUT, initial = GPIO.LOW)
        GPIO.setup(cls.ECHO, GPIO.IN)
    
    @classmethod
    def clean_gpio(cls):
        GPIO.cleanup([cls.TRIG, cls.ECHO])
