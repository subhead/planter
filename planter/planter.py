# Imports
import time
import os
import board
from pprint import pprint
from datetime import datetime
from dynaconf import settings
import adafruit_dht
import psycopg2
import subprocess
import argparse
import threading
import paho.mqtt.publish as mqtt_publish


# Load config
settings.setenv("APP")
USE_DOCKER = settings.USE_DOCKER
GPIO_LIST = settings.GPIO_LIST
USE_DATABASE = settings.USE_DATABASE
USE_GPIO = settings.USE_GPIO
USE_WEBCAM = settings.USE_WEBCAM
USE_MQTT = settings.USE_MQTT
WEBCAM_INTERVAL = settings.WEBCAM_INTERVAL
WEBCAM_OUTPUT_PATH = os.getcwd() + os.path.sep + 'data' + os.path.sep + 'images'
WEBCAM_DEVICE = settings.WEBCAM_DEVICE
WEBCAM_USE_PNG = settings.WEBCAM_USE_PNG
WEBCAM_RESOLUTION = settings.WEBCAM_RESOLUTION
WEBCAM_EXTRA_ARGS = settings.WEBCAM_EXTRA_ARGS
WEBCAM_TIMELAPSE = settings.WEBCAM_TIMELAPSE
SLEEP = settings.as_float('SLEEP')
POSTGRES_HOST = settings.POSTGRES_HOST
POSTGRES_PORT = settings.POSTGRES_PORT
POSTGRES_SCHEMA = settings.POSTGRES_SCHEMA
POSTGRES_USERNAME = settings.POSTGRES_USERNAME
POSTGRES_PASSWORD = settings.POSTGRES_PASSWORD
POSTGRES_DATABASE = settings.POSTGRES_DATABASE
MQTT_SERVER_HOST = settings.MQTT_SERVER_HOST
MQTT_SERVER_PORT = settings.MQTT_SERVER_PORT
MQTT_SERVER_USERNAME = settings.MQTT_SERVER_USERNAME
MQTT_SERVER_PASSWORD = settings.MQTT_SERVER_PASSWORD
MQTT_SERVER_TOPIC = settings.MQTT_SERVER_TOPIC


# Functions
def webcam_take_picture():

	timelapse = True
	
	while timelapse == True:
		try:
			timelapse = WEBCAM_TIMELAPSE
			# See if we should use ong otherwise switch to jpg as fallback
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
			print("Picture: {} captured.".format(outfile))
			# Check if we should run in timelapse mode otherwise exit the loop
			if not WEBCAM_TIMELAPSE:
				timelapse = False
			else:
				time.sleep(WEBCAM_INTERVAL)

def webinterface_start():
	try:
		command = "FLASK_APP=dashboard.py FLASK_ENV=production flask run --host=0.0.0.0 --port=5000"
		ui = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
		ui.wait()
	except subprocess.CalledProcessError:
		print("Starting webinterface failed.")


def sensor_run(sensor_pin, sensor_desc, mode=""):
	endless = True

	# Initial the dht device, with data pin connected to:
	dhtDevice = adafruit_dht.DHT22(eval(sensor_pin))

	while endless == True:
		try:
			if mode is not "monitor":
				endless = False
			
			current_datetime = datetime.utcnow()
			# Print the values to the serial port
			temperature_c = dhtDevice.temperature
			temperature_f = temperature_c * (9 / 5) + 32
			humidity = dhtDevice.humidity

			if humidity <= 100:
				# send to mqtt backend
				if USE_MQTT:
					mqtt_messages = [
						{f'topic': MQTT_SERVER_TOPIC + f"/{sensor_desc}/temperatur".lower().replace(" ", "_"), 'payload': temperature_c, 'qos': 0, 'retain': True},
						{f'topic': MQTT_SERVER_TOPIC + f"/{sensor_desc}/humidity".lower().replace(" ", "_"), 'payload': humidity, 'qos': 0, 'retain': True}
					]
					mqtt_auth = dict(username=MQTT_SERVER_USERNAME, password=MQTT_SERVER_PASSWORD)
					mqtt_publish.multiple(
						mqtt_messages,
						hostname=MQTT_SERVER_HOST,
						port=MQTT_SERVER_PORT,
						client_id="planter-backend",
						will=None,
						auth=mqtt_auth,
						tls=None,
						transport="tcp"
					)

				# database thingy
				if USE_DATABASE:			
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
									(temp_date, temp_fahrenheit, temp_celcius, temp_humidity, temp_sensor_desc, temp_sensor_pin)
									VALUES (%s, %s, %s, %s, %s, %s) """							
								cursor.execute(query, (current_datetime, temperature_f, temperature_c, humidity, sensor_desc, sensor_pin))

					except(Exception, psycopg2.Error) as error:
						print(error)
					finally:
						# closing db connection
						if(conn):
							print("Sensor: {} / Temp: {:.1f} F / {:.1f} C    Humidity: {}% "
								.format(sensor_desc +'/'+ sensor_pin, temperature_f, temperature_c, humidity))
							conn.close()

			else:
				print("Sensor: {} / Temp: {:.1f} F / {:.1f} C    Humidity: {}% "
					.format(pin_desc, temperature_f, temperature_c, humidity))
				
		except RuntimeError as error:
			# Errors happen fairly often, DHT's are hard to read, just keep going
			print(error.args[0])
			
		if mode == "monitor":
			time.sleep(SLEEP)

def container_start():
	try:
		current_datetime = datetime.utcnow()
		compose_file = os.getcwd() + os.path.sep + "docker-compose.yml"
		print(compose_file)
		#command = f"docker-compose -f "
		#capture = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
		#capture.wait()
	except subprocess.CalledProcessError:
		print("Capturing image failed.")
	finally:
		print("Picture: captured.")
		# Check if we should run in timelapse mode otherwise exit the loop
		

if __name__ == '__main__':
	
	parser = argparse.ArgumentParser()
	parser.add_argument("-sensors", "-s", "--sensors", help="Returns the readings from all configured sensors", action="store_true")
	parser.add_argument("-camera", "-c", "--camera", help="Captures an image from configured video device.", action="store_true")
	parser.add_argument("-monitor", "-m", "--monitor", help="Start the monitor which runs until stopped", action="store_true")
	parser.add_argument("-webinterface", "-w", "--webinterface", help="Starts the monitoring webinterface", action="store_true")
	args = parser.parse_args()

	#if USE_DOCKER:
	#	container_start()

	th = []

	if args.webinterface:
		p_ui = threading.Thread(target=webinterface_start)
		th.append(p_ui)
		p_ui.start()

	if args.camera:
		if USE_WEBCAM:
			p_cam = threading.Thread(target=webcam_take_picture).start()

	if args.sensors:
		for gpio_pin in settings.get('GPIO'):
			pin_id,pin_desc = settings.get('GPIO').get(gpio_pin).split(',')
			GPIO = 'board.' + pin_id	
			p_gpio = threading.Thread(target=sensor_run, args=(GPIO, pin_desc, "monitor",))
			th.append(p_gpio)
			p_gpio.start()

		if th is not None:
			for t in th:
				t.join()

	if args.monitor:
		if USE_WEBCAM:
			p_cam = threading.Thread(target=webcam_take_picture)
			th.append(p_cam)
			p_cam.start()
		if USE_GPIO:
			for gpio_pin in settings.get('GPIO'):
				pin_id,pin_desc = settings.get('GPIO').get(gpio_pin).split(',')
				GPIO = 'board.' + pin_id	
				p_gpio = threading.Thread(target=sensor_run, args=(GPIO, pin_desc, "monitor",))
				th.append(p_gpio)
				p_gpio.start()
			
	if th is not None:
		for t in th:
			t.join()



