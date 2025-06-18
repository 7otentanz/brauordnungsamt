import RPi.GPIO as GPIO
import time

def undlos():

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(5, GPIO.OUT)
    GPIO.setup(6, GPIO.OUT)

    GPIO.output(6, GPIO.LOW)
    time.sleep(2)
    GPIO.output(6, GPIO.HIGH)
    GPIO.output(5, GPIO.LOW)
    time.sleep(2)
    GPIO.output(5, GPIO.HIGH)
    time.sleep(2)
    GPIO.output(6, GPIO.LOW)
    GPIO.output(5, GPIO.LOW)
    time.sleep(2)
    GPIO.output(6, GPIO.HIGH)
    GPIO.output(5, GPIO.HIGH)

GPIO.cleanup()
