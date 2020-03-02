from datetime import datetime
from dashboard import db

class temperatur(db.Model):
	temp_id = db.Column(db.Integer, primary_key=True)
	temp_date = db.Column(db.DateTime, default=datetime.utcnow)
	temp_fahrenheit = db.Column(db.Float)
	temp_celcius = db.Column(db.Float)
	temp_humidity = db.Column(db.Float)
	temp_sensor_desc = db.Column(db.String(100))
	temp_sensor_pin = db.Column(db.String(25))
	
	def __repr__(self):
		return f'<Sensor {temp_sensor_pin} Desc {temp_sensor_desc} Date {temp_date.strftime("%Y-%m-%d %H:%M:%S")} Temp {temp_fahrenheit}/{temp_celcius} Hum {temp_humidity}'