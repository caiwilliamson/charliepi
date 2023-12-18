import RPi.GPIO as GPIO


class LED:
    def __init__(self, pin=None):
        self._pin = pin

        if self._pin is not None:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self._pin, GPIO.OUT, initial=GPIO.LOW)

    def toggle(self):
        if self._pin is not None:
            GPIO.output(self._pin, not GPIO.input(self._pin))

    def cleanup(self):
        if self._pin is not None:
            GPIO.cleanup(self._pin)
