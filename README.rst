Raspi Robot
===========

.. image:: https://img.shields.io/badge/license-GPL-blue.svg
    :target: https://github.com/veryplay/raspi-robot
    :alt: License

.. image:: https://img.shields.io/badge/build-passing-green.svg
    :target: https://github.com/veryplay/raspi-robot
    :alt: Build Status

.. image:: https://img.shields.io/badge/python-2.7%20%7C%203.6-blue.svg
	:target:  https://github.com/veryplay/raspi-robot
	:alt: Python Versions


Raspi Robot is a simple python program for raspberry 3B, include Motor Shield(L298N), Ultrasonic Sensor(HC-SR04) component.


Motor Shield(L298N) Interface
-----------------------------

.. image:: ./docs/L298N.png

Connection Detail of Motor Shield(L298N)
----------------------------------------

.. image:: ./docs/L298N_AND_RASPI.png


Connection Detail of Ultrasonic Sensor(HC-SR04)
-----------------------------------------------

.. image:: ./docs/HC-SR04.png


Usage
-----

.. code:: bash

    python raspi_robot/robot.py

Note
----

Need to change L298N/HC-SR04's actual GPIO port in ``driver.py``、``decelerator.py``、``ultrasonic.py``.


.. table:: L298N connection detail

   =====  =======
   L298N   GPIO
   =====  =======
   IN1    GPIO 05
   IN2    GPIO 06
   IN3    GPIO 13
   IN4    GPIO 26
   =====  =======
   ENA    GPIO 18
   ENB    GPIO 19
   =====  =======

.. table:: HC-SR04 connection detail

   =====  =======
   L298N   GPIO
   =====  =======
    VCC   GPIO 5V
   TRIG   GPIO 23
   ECHO   GPIO 24
    GND   GPIO GND
   =====  =======