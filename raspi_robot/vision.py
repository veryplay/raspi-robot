#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
import logging
import Queue
from Queue import Empty
from picamera import PiCamera
import time
from threading import Thread

from lifecycle import LifeCycle

logger = logging.getLogger(__name__)

DEFAULR_DATE_FORMAT="%Y-%m-%d"

class Vision(LifeCycle):

    CACHE_LENGTH = 10

    def __init__(self):
        super(Vision, self).__init__()
        self.camera = PiCamera()
        self.camera.resolution = (640, 480)

    def do_start(self):
        self.queue = Queue.Queue(self.CACHE_LENGTH)

        self.vs_thread = Thread(name = "VisionThread", target = self.run)
        self.vs_thread.start()
        logger.info("start completely.")
    
    def do_stop(self):
        while (hasattr(self, "vs_thread") 
            and self.vs_thread 
            and self.vs_thread.isAlive()):
            self.vs_thread.join(1)
            logger.warn("wait %s to finish.", self.vs_thread.getName())
        
        self.queue.queue.clear()
        logger.info("stop completely.")

    def run(self):
        while not self.should_stop():
            try:
                anything = self.queue.get(block = True, timeout = 0.01)
                if anything:
                    self.capture()
            except Queue.Empty:
                continue
            except Exception:
                logger.error("VisionThread run failed.", exc_info=1)

    def trigger_vision_event(self):
        try:
            self.queue.put_nowait(True)
        except Queue.Full:
                logger.warn("Vision Queue is full, ignore it.")

    def capture(self):
        self.camera.start_preview()
        time.sleep(2)
        picture_filename = self.generate_picture_filename()
        self.camera.capture('/home/pi/%s' % picture_filename)
        self.camera.stop_preview()

    def generate_picture_filename(self):
        d = datetime.now()
        ds = d.strftime(DEFAULR_DATE_FORMAT)
        dm = int(time.time() * 1000)
        return "%s_%d.jpg" % (ds, dm)
