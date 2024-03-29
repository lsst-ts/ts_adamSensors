__all__ = ["CONFIG_SCHEMA"]

import yaml


CONFIG_SCHEMA = yaml.safe_load(
    """
$schema: http://json-schema.org/draft-07/schema#
$id: https://github.com/lsst-ts/ts_adamSensors/blob/master/schema/AdamSensors.yaml
# title must end with one or more spaces followed by the schema version, which must begin with "v"
title: AdamSensors v1
description: Schema for ts_adamSensors configuration files
type: object
properties:
  adam_ip:
    description: IP of the ADAM controller.
    type: string
    default: "127.0.0.1"
  adam_port:
    description: port of the ADAM controller.
    type: number
    default: 502
  analog_input_0_type:
    description: Type of sensor connected to ADAM AO-0. Can be "None", "Temperature", or "Pressure".
    type: string
    default: "None"
    enum: ["Temperature", "Pressure", "None"]
  analog_input_0_coefficients:
    description: >-
      list of numbers defining, in descending order, the terms of a polynomial that maps voltages
      to the appropriate units. A value of [1., 0] here is a 1:1 linear mapping of volts to whatever.
    type: array
    items:
      type: number
    default: [1., 0.]
  analog_input_1_type:
    description: Type of sensor connected to ADAM AO-1. Can be "None", "Temperature", or "Pressure".
    type: string
    default: "None"
    enum: ["Temperature", "Pressure", "None"]
  analog_input_1_coefficients:
    description: >-
      list of numbers defining, in descending order, the terms of a polynomial that maps voltages
      to the appropriate units. A value of [1., 0] here is a 1:1 linear mapping of volts to whatever.
    type: array
    items:
      type: number
    default: [1., 0.]
  analog_input_2_type:
    description: Type of sensor connected to ADAM AO-2. Can be "None", "Temperature", or "Pressure".
    type: string
    default: "None"
    enum: ["Temperature", "Pressure", "None"]
  analog_input_2_coefficients:
    description: >-
      list of numbers defining, in descending order, the terms of a polynomial that maps voltages
      to the appropriate units. A value of [1., 0] here is a 1:1 linear mapping of volts to whatever.
    type: array
    items:
      type: number
    default: [1., 0.]
  analog_input_3_type:
    description: Type of sensor connected to ADAM AO-3. Can be "None", "Temperature", or "Pressure".
    type: string
    default: "None"
    enum: ["Temperature", "Pressure", "None"]
  analog_input_3_coefficients:
    description: >-
      list of numbers defining, in descending order, the terms of a polynomial that maps voltages
      to the appropriate units. A value of [1., 0] here is a 1:1 linear mapping of volts to whatever.
    type: array
    items:
      type: number
    default: [344738., 0.]
  analog_input_4_type:
    description: Type of sensor connected to ADAM AO-4. Can be "None", "Temperature", or "Pressure".
    type: string
    default: "None"
    enum: ["Temperature", "Pressure", "None"]
  analog_input_4_coefficients:
    description: >-
      list of numbers defining, in descending order, the terms of a polynomial that maps voltages
      to the appropriate units. A value of [1., 0] here is a 1:1 linear mapping of volts to whatever.
    type: array
    items:
      type: number
    default: [1., 0.]
  analog_input_5_type:
    description: Type of sensor connected to ADAM AO-5. Can be "None", "Temperature", or "Pressure".
    type: string
    default: "None"
    enum: ["Temperature", "Pressure", "None"]
  analog_input_5_coefficients:
    description: >-
      list of numbers defining, in descending order, the terms of a polynomial that maps voltages
      to the appropriate units. A value of [1., 0] here is a 1:1 linear mapping of volts to whatever.
    type: array
    items:
      type: number
    default: [344738., 0.]"""
)
