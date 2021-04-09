from lsst.ts import salobj
from lsst.ts.adamSensors.model import AdamModel
from numpy import poly1d
import asyncio
from pymodbus.exceptions import ConnectionException
from .config_schema import CONFIG_SCHEMA
from .version import __version__


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

        self.adam = None
        self.config = None
        self.start_timeout = 10

        self.telemetry_loop_task = salobj.make_done_future()

    async def begin_start(self, data):
        """
        Sets up the model which communicates with the ADAM hardware, and
        initiates the telemetry publishing loop
        """
        self.cmd_start.ack_in_progress(data, timeout=self.start_timeout)
        await super().begin_start(data)
        self.adam = AdamModel(self.log, simulation_mode=self.simulation_mode)
        try:
            await self.adam.connect(self.config.adam_ip, self.config.adam_port)
        except ConnectionException:
            raise RuntimeError(f"Unable to connect to modbus device at {self.config.adam_ip}:\
                {self.config.adam_port}.")
        if self.telemetry_loop_task.result() is not None:
            self.telemetry_loop_task.cancel()
        self.telemetry_loop_task = asyncio.create_task(self.telemetry_loop())

    async def end_standby(self, data):
        """
        When transitioning from disabled or fault state to standby,
        cancels the telemetry loop task and disconnects from the ADAM
        device.
        """
        try:
            self.telemetry_loop_task.cancel()
            await self.model.disconnect()
        except:
            pass

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
        while True:
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

    @staticmethod
    def get_config_pkg():
        return "ts_config_eas"

    async def configure(self, config):
        self.config = config
