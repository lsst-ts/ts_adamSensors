from lsst.ts import salobj
from lsst.ts.adamSensors.model import AdamModel
from numpy import poly1d
import asyncio
import logging
from pymodbus.exceptions import ConnectionException
from .config_schema import CONFIG_SCHEMA
from . import __version__


class AdamCSC(salobj.ConfigurableCsc):
    """
    CSC for simple sensors connected to an ADAM controller
    """

    version = __version__
    valid_simulation_modes = (0, 1)

    def __init__(
        self, config_dir=None, initial_state=salobj.State.STANDBY, simulation_mode=0
    ):
        super().__init__(
            "AdamSensors",
            index=0,
            config_schema=CONFIG_SCHEMA,
            config_dir=config_dir,
            initial_state=initial_state,
            simulation_mode=simulation_mode,
        )

        self.log.addHandler(logging.StreamHandler())
        self.log.setLevel(logging.DEBUG)

        self.loop = asyncio.get_running_loop()

        self.adam = None
        self.config = None
        self.start_timeout = 10

        self.telemetry_loop_task = salobj.make_done_future()

    async def handle_summary_state(self):
        if self.disabled_or_enabled:
            if self.adam is None:
                try:
                    self.adam = AdamModel(
                        self.config.adam_ip,
                        self.config.adam_port,
                        log=self.log,
                        simulation_mode=self.simulation_mode,
                    )
                    self.log.debug("model created")
                except ConnectionException:
                    raise RuntimeError(
                        "Unable to connect to modbus device at "
                        f"{self.config.adam_ip}:{self.config.adam_port}."
                    )
                except Exception:
                    self.log.exception("Error connecting to modbus.")
                    raise
                self.log.debug(f"connected to modbus device at {self.adam.clientip}:{self.adam.clientport}")
                if self.telemetry_loop_task.done():
                    self.log.debug("starting telemetry loop")
                    self.telemetry_loop_task = asyncio.create_task(
                        self.telemetry_loop()
                    )
            self.log.debug("done setting up CSC for disabled or enabled state")
        else:
            if not self.telemetry_loop_task.done():
                self.telemetry_loop_task.cancel()
            try:
                await self.telemetry_loop_task
            except asyncio.CancelledError:
                pass
            except Exception:
                self.log.exception(
                    f"Exception awaiting telemetry loop while in state {self.summary_state}"
                )
            if self.adam is not None:
                await self.adam.disconnect()
                self.adam = None

    async def telemetry_loop(self):
        """
        The main process of this CSC, periodically reads the voltages off
        the ADAM device, converts them into the appropriate units
        for various sensor types, and publishes them as telemetry
        """
        # set up dictionary
        sensors = {
            0: (
                self.config.analog_input_0_type,
                poly1d(self.config.analog_input_0_coefficients),
            ),
            1: (
                self.config.analog_input_1_type,
                poly1d(self.config.analog_input_1_coefficients),
            ),
            2: (
                self.config.analog_input_2_type,
                poly1d(self.config.analog_input_2_coefficients),
            ),
            3: (
                self.config.analog_input_3_type,
                poly1d(self.config.analog_input_3_coefficients),
            ),
            4: (
                self.config.analog_input_4_type,
                poly1d(self.config.analog_input_4_coefficients),
            ),
            5: (
                self.config.analog_input_5_type,
                poly1d(self.config.analog_input_5_coefficients),
            ),
        }

        # figure out which topics to publish
        hasTemperature = False
        hasPressure = False
        for s in sensors:
            if sensors[s][0] == "Pressure":
                hasPressure = True
            if sensors[s][0] == "Temperature":
                hasTemperature = True

        self.log.debug("hasPressure = " + str(hasPressure))

        outputs = [0, 0, 0, 0, 0, 0]
        self.log.debug("about to start telemetry loop")
        while self.adam is not None:
            voltages = await self.adam.read_voltage()
            # convert the voltage into appropriate units, according to the
            # polynomial defined in configuration
            for i in range(6):
                outputs[i] = sensors[i][1](voltages[i])

            # Assemble telemetry topics
            # Channel 0
            if sensors[0][0] == "Pressure":
                self.tel_pressure.set(pressure_ch0=outputs[0])
            elif sensors[0][0] == "Temperature":
                self.tel_temperature.set(temp_ch0=outputs[0])

            # Channel 1
            if sensors[1][0] == "Pressure":
                self.tel_pressure.set(pressure_ch1=outputs[1])
            elif sensors[1][0] == "Temperature":
                self.tel_temperature.set(temp_ch1=outputs[1])

            # Channel 2
            if sensors[2][0] == "Pressure":
                self.tel_pressure.set(pressure_ch2=outputs[2])
            elif sensors[2][0] == "Temperature":
                self.tel_temperature.set(temp_ch2=outputs[2])

            # Channel 3
            if sensors[3][0] == "Pressure":
                self.tel_pressure.set(pressure_ch3=outputs[3])
            elif sensors[3][0] == "Temperature":
                self.tel_temperature.set(temp_ch3=outputs[3])

            # Channel 4
            if sensors[4][0] == "Pressure":
                self.tel_pressure.set(pressure_ch4=outputs[4])
            elif sensors[4][0] == "Temperature":
                self.tel_temperature.set(temp_ch4=outputs[4])

            # Channel 5
            if sensors[5][0] == "Pressure":
                self.tel_pressure.set(pressure_ch5=outputs[5])
            elif sensors[5][0] == "Temperature":
                self.tel_temperature.set(temp_ch5=outputs[5])

            # publish telemetry
            if hasPressure:
                self.log.debug("publishing pressure")
                self.tel_pressure.put()
            if hasTemperature:
                self.log.debug("publishing temperature")
                self.tel_temperature.put()

            await asyncio.sleep(self.heartbeat_interval)
        self.log.debug("aborted loop because the model was None")

    @staticmethod
    def get_config_pkg():
        return "ts_config_eas"

    async def configure(self, config):
        self.config = config
