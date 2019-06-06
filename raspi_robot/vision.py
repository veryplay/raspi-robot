#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
import logging
from picamera import PiCamera
import time

from lifecycle import LifeCycle

logger = logging.getLogger(__name__)

DEFAULR_DATE_FORMAT="%Y-%m-%d"

class Vision(LifeCycle):

    def __init__(self):
        super(Vision, self).__init__()
        self.camera = PiCamera()
        self.camera.resolution = (640, 480)

    def do_start(self):
        logger.info("start completely.")
    
    def do_stop(self):
        logger.info("stop completely.")

    def capture(self):
        self.camera.start_preview()
        time.sleep(2)
        picture_filename = self.generate_picture_filename()
        self.camera.capture('/home/pi/%s' % picture_filename)
        self.camera.stop_preview()

    def record(self):
        self.camera.start_preview()
        video_filename = self.generate_video_filename()
        self.camera.start_recording('/home/pi/%s' % video_filename)
        time.sleep(10)
        self.camera.stop_recording()
        self.camera.stop_preview()

    def generate_picture_filename(self):
        d = datetime.now()
        ds = d.strftime(DEFAULR_DATE_FORMAT)
        dm = int(time.time() * 1000)
        return "%s_%d.jpg" % (ds, dm)

    def generate_video_filename(self):
        d = datetime.now()
        ds = d.strftime(DEFAULR_DATE_FORMAT)
        dm = int(time.time() * 1000)
        return "%s_%d.h264" % (ds, dm)