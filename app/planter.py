import time
from dynaconf import settings
import os
import board
import adafruit_dht

# Console colors
W = '\033[0m'  # white (normal)
R = '\033[31m'  # red
G = '\033[32m'  # green
O = '\033[33m'  # orange
B = '\033[34m'  # blue
P = '\033[35m'  # purple
C = '\033[36m'  # cyan
GR = '\033[37m'  # gray

settings.setenv("APP")
print(settings.GPIO)
USE_DATABASE = settings.USE_DATABASE
USE_GPIO = settings.USE_GPIO
USE_WEBCAM = settings.USE_WEBCAM
SLEEP = settings.as_float('SLEEP')
POSTGRES_HOST = settings.POSTGRES_HOST
POSTGRES_PORT = settings.POSTGRES_PORT
POSTGRES_SCHEMA = settings.POSTGRES_SCHEMA
POSTGRES_USERNAME = settings.POSTGRES_USERNAME
POSTGRES_PASSWORD = settings.POSTGRES_PASSWORD


GPIO = {}

for gpio_pin in settings.GPIO:
	GPIO[gpio_pin] = eval('settings.GPIO.'+gpio_pin)
	#print(eval('settings.GPIO.' + gpio_pin))

#print(GPIO)
#GPIO = 'board.'+pin
	
# Initial the dht device, with data pin connected to:
#dhtDevice = adafruit_dht.DHT22(eval(GPIO))
	
#while True:
#	try:
#		# Print the values to the serial port
#		temperature_c = dhtDevice.temperature
#		temperature_f = temperature_c * (9 / 5) + 32
#		humidity = dhtDevice.humidity
#		print("Temp: {:.1f} F / {:.1f} C    Humidity: {}% "
#				.format(temperature_f, temperature_c, humidity))
#	
#	except RuntimeError as error:
#		# Errors happen fairly often, DHT's are hard to read, just keep going
#		print(error.args[0])
#	
#	time.sleep(SLEEP)


