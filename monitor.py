import time
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
	
# Initial the dht device, with data pin connected to:
dhtDevice = adafruit_dht.DHT22(board.D18)
	
while True:
	try:
		# Print the values to the serial port
		temperature_c = dhtDevice.temperature
		temperature_f = temperature_c * (9 / 5) + 32
		humidity = dhtDevice.humidity
		print("Temp: {:.1f} F / {:.1f} C    Humidity: {}% "
				.format(temperature_f, temperature_c, humidity))
	
	except RuntimeError as error:
		# Errors happen fairly often, DHT's are hard to read, just keep going
		print(error.args[0])
	
	time.sleep(2.0)