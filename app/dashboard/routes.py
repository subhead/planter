import datetime
import time
from os.path import altsep
from pprint import pprint

from dashboard import dashboard
from dashboard.models import temperatur
from flask import jsonify, render_template



@dashboard.route('/')
@dashboard.route('/index')
def index():
	header_text = 'Hey gringo!'

	#tableTempHistory = temperatur.query.order_by(temperatur.temp_date.desc()).all()
	tableTempHistory = temperatur.query.order_by(temperatur.temp_date.desc()).limit(8650).all()

	sn_tmp = []
	# extract sensor names
	for sn in tableTempHistory:
		sn_tmp.append(sn.temp_sensor_desc)

	# get sensor pins	
	sp_tmp = []
	for sp in tableTempHistory:
		sp_tmp.append(sp.temp_sensor_pin)

	# get humidity and dates
	hum_data = []
	for hum in tableTempHistory:
		hum_data.append({'date': hum.temp_date.strftime("%Y-%m-%d %H:%M:%S"), 'sensor_desc': hum.temp_sensor_desc, 'sensor_pin': hum.temp_sensor_pin, 'x': int(time.mktime(hum.temp_date.timetuple())) * 1000, 'y': hum.temp_humidity})

	# iterate over sensors
	temp_data = []
	for temp in tableTempHistory:
		temp_data.append({'date': temp.temp_date.strftime("%Y-%m-%d %H:%M:%S"), 'sensor_desc': temp.temp_sensor_desc, 'sensor_pin': temp.temp_sensor_pin,'x': int(time.mktime(temp.temp_date.timetuple())) * 1000, 'y': temp.temp_celcius})

	# chart
	chart_labels = sorted(set(sn_tmp))

	return render_template(
		'index.html',
		header_text=header_text,
		historicData=tableTempHistory,
		chart_labels=chart_labels,
		temp_chart_values=temp_data,
		hum_chart_values=hum_data
	)


@dashboard.route('/logs')
def logs():
	header_text = "Logs"

	return render_template(
		'index.html',
		header_text=header_text,
		historicData=tableTempHistory,
		pagination=pagination,
		chart_legend=chart_legend,
		chart_labels=chart_labels,
		chart_values=chart_values
	)
