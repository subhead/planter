import time
from dynaconf import settings
import os
import board
import adafruit_dht
from pprint import pprint
import psycopg2
from datetime import datetime

settings.setenv("APP")
GPIO_LIST = settings.GPIO_LIST
USE_DATABASE = settings.USE_DATABASE
USE_GPIO = settings.USE_GPIO
USE_WEBCAM = settings.USE_WEBCAM
SLEEP = settings.as_float('SLEEP')
POSTGRES_HOST = settings.POSTGRES_HOST
POSTGRES_PORT = settings.POSTGRES_PORT
POSTGRES_SCHEMA = settings.POSTGRES_SCHEMA
POSTGRES_USERNAME = settings.POSTGRES_USERNAME
POSTGRES_PASSWORD = settings.POSTGRES_PASSWORD
POSTGRES_DATABASE = settings.POSTGRES_DATABASE


for gpio_pin in settings.get('GPIO'):
	pin_id,pin_desc = settings.get('GPIO').get(gpio_pin).split(',')


GPIO = 'board.' + pin_id

# Initial the dht device, with data pin connected to:
dhtDevice = adafruit_dht.DHT22(eval(GPIO))
	
while True:
	try:
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
					log.error(f'Dude where is my database?: {error}')
				finally:
					# closing db connection
					if(conn):
						print("Sensor: {} / Temp: {:.1f} F / {:.1f} C    Humidity: {}% "
							.format(pin_desc, temperature_f, temperature_c, humidity))
						conn.close()
						#log.debug(f"Database ({POSTGRES_DATABASE}) connection successfully closed.")

		else:
			print("Sensor: {} / Temp: {:.1f} F / {:.1f} C    Humidity: {}% "
				.format(pin_desc, temperature_f, temperature_c, humidity))
	
	except RuntimeError as error:
		# Errors happen fairly often, DHT's are hard to read, just keep going
		print(error.args[0])
	
	time.sleep(SLEEP)


