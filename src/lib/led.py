import RPi.GPIO as GPIO


class LED:
    def __init__(self, pin=None):
        self.pin = pin
        if self.pin is not None:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pin, GPIO.OUT, initial=GPIO.LOW)

    def toggle(self):
        if self.pin is not None:
            GPIO.output(self.pin, not GPIO.input(self.pin))

    def cleanup(self):
        if self.pin is not None:
            GPIO.cleanup(self.pin)
