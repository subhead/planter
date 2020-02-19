-- DROP SCHEMA planter;

CREATE SCHEMA IF NOT EXISTS planter AUTHORIZATION planter;

-- Drop table

-- DROP TABLE planter.temperatur;

CREATE TABLE IF NOT EXISTS planter.temperatur (
	temp_id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
	temp_date timestamp NULL,
	temp_fahrenheit float4 NULL,
	temp_celcius float4 NULL,
	temp_humidity float4 NULL,
	temp_sensor_desc varchar(100) NULL,
	temp_sensor_pin varchat(25) NULL
);

ALTER DATABASE planter OWNER TO planter;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA planter TO planter;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA planter TO planter;