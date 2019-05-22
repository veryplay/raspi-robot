#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import logging.config
import time
from signal import pause

here = os.path.abspath(os.path.dirname(__file__))
log_config_file = os.path.join(here, "logging.conf")
logging.config.fileConfig(log_config_file, disable_existing_loggers = False)

from driver import Driver

ascii_snake = """\
=============================================================================================

    --..,_                     _,.--.
       `'.'.                .'`__ o  `;__. 
          '.'.            .'.'`  '---'`  `  Raspi Robot
            '.`'--....--'`.'
              `'--....--'`

=============================================================================================
"""

logger = logging.getLogger(__name__)

def run():
    print ascii_snake

    d = Driver()
    d.start()
    logger.info("robot is ready to go.")

    pause()
    
if __name__ == '__main__':
    run()