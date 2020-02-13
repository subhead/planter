import time
from dynaconf import settings
import os
import board
import adafruit_dht
from pprint import pprint
import psycopg2
from datetime import datetime
import subprocess
import argparse

# Load config
settings.setenv("APP")
GPIO_LIST = settings.GPIO_LIST
USE_DATABASE = settings.USE_DATABASE
USE_GPIO = settings.USE_GPIO
USE_WEBCAM = settings.USE_WEBCAM
WEBCAM_INTERVAL = settings.WEBCAM_INTERVAL
WEBCAM_OUTPUT_PATH = os.getcwd() + os.path.sep + 'data' + os.path.sep + 'images'
WEBCAM_DEVICE = settings.WEBCAM_DEVICE
WEBCAM_USE_PNG = settings.WEBCAM_USE_PNG
WEBCAM_RESOLUTION = settings.WEBCAM_RESOLUTION
WEBCAM_EXTRA_ARGS = settings.WEBCAM_EXTRA_ARGS
SLEEP = settings.as_float('SLEEP')
POSTGRES_HOST = settings.POSTGRES_HOST
POSTGRES_PORT = settings.POSTGRES_PORT
POSTGRES_SCHEMA = settings.POSTGRES_SCHEMA
POSTGRES_USERNAME = settings.POSTGRES_USERNAME
POSTGRES_PASSWORD = settings.POSTGRES_PASSWORD
POSTGRES_DATABASE = settings.POSTGRES_DATABASE

# Functions
def webcam_take_picture():
	try:		
		if WEBCAM_USE_PNG:
			picture_format = '--png 9'
			file_extension = '.png'
		else:
			picture_format = '--jpeg 95'
			file_extension = '.jpg'

		current_datetime = datetime.utcnow()
		outfile = WEBCAM_OUTPUT_PATH + os.path.sep + 'capture-' + str(current_datetime).replace(':', '_').replace('.', '_').replace(' ', '_').replace('-', '_') + file_extension

		command = f"fswebcam {WEBCAM_EXTRA_ARGS} -r {WEBCAM_RESOLUTION} -d v4l2:{WEBCAM_DEVICE} {picture_format} --save {outfile}"
		capture = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
		capture.wait()
	except subprocess.CalledProcessError:
		print("Capturing image failed.")
	finally:
		print("Picture {} captured.".format(outfile))


def sensor_run(mode=""):
	
	endless = True
	
	for gpio_pin in settings.get('GPIO'):
		pin_id,pin_desc = settings.get('GPIO').get(gpio_pin).split(',')

	GPIO = 'board.' + pin_id

	# Initial the dht device, with data pin connected to:
	dhtDevice = adafruit_dht.DHT22(eval(GPIO))

	while endless == True:
		try:
			if mode is not "monitor":
				endless = False
			
			current_datetime = datetime.utcnow()
			# Print the values to the serial port
			temperature_c = dhtDevice.temperature
			temperature_f = temperature_c * (9 / 5) + 32
			humidity = dhtDevice.humidity

			# database thingy
			if USE_DATABASE:
				if humidity > 0:
					# init database connection
					try:
						conn = psycopg2.connect(
							user = POSTGRES_USERNAME,
							password = POSTGRES_PASSWORD,
							host = POSTGRES_HOST,
							port = POSTGRES_PORT,
							database = POSTGRES_DATABASE
						)

						with conn:
							with conn.cursor() as cursor:
								query = """INSERT INTO "temperatur" 
									(temp_date, temp_fahrenheit, temp_celcius, temp_humidity, temp_sensor)
									VALUES (%s, %s, %s, %s, %s) """							
								cursor.execute(query, (current_datetime, temperature_f, temperature_c, humidity, pin_desc))

					except(Exception, psycopg2.Error) as error:
						print("Sensor: {} / Temp: {:.1f} F / {:.1f} C    Humidity: {}% "
						.format(pin_desc, temperature_f, temperature_c, humidity))
					finally:
						# closing db connection
						if(conn):
							print("Sensor: {} / Temp: {:.1f} F / {:.1f} C    Humidity: {}% "
								.format(pin_desc, temperature_f, temperature_c, humidity))
							conn.close()

			else:
				print("Sensor: {} / Temp: {:.1f} F / {:.1f} C    Humidity: {}% "
					.format(pin_desc, temperature_f, temperature_c, humidity))
				
		except RuntimeError as error:
			# Errors happen fairly often, DHT's are hard to read, just keep going
			print(error.args[0])
		if mode == "monitor":
			time.sleep(SLEEP)




if __name__ == '__main__':
	
	parser = argparse.ArgumentParser()
	parser.add_argument("-sensors", "-s", "--sensors", help="Returns the readings from all configured sensors", action="store_true")
	parser.add_argument("-camera", "-c", "--camera", help="Captures an image from configured video device.", action="store_true")
	parser.add_argument("-monitor", "-m", "--monitor", help="Start the monitor which runs until stopped", action="store_true")
	args = parser.parse_args()
	# debug
	pprint(args)

	if args.camera:
		webcam_take_picture()

	if args.sensors:
		sensor_run()

	if args.monitor:
		while True:
			sensor_run(mode="monitor")
	
