#################
ts_adamSensors
#################


Provides the ability to read temperatures and pressures from transducer type sensors connected to an ADAM-6024 or similar modbus device. For each of the ADAM's six channels, the configuration file allows you to set a device type of "Temperature" "Pressure" or "None", and to specify a polynomial function to map the voltage readings (in the range of -10 to 10) onto degrees C or pascals.