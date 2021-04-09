import unittest
import asynctest
import asyncio
import pathlib

from lsst.ts import salobj
from lsst.ts import adamSensors


STD_TIMEOUT = 15  # standard command timeout (sec)
TEST_CONFIG_DIR = pathlib.Path(__file__).parents[1].joinpath("tests", "data", "config")


class CscTestCase(salobj.BaseCscTestCase, asynctest.TestCase):
    def basic_make_csc(self, initial_state, config_dir, simulation_mode):
        return adamSensors.adamSensorsCSC.AdamCSC(
            initial_state=initial_state,
            config_dir=config_dir,
            simulation_mode=simulation_mode,
        )

    async def test_state_transitions(self):
        async with self.make_csc(
            initial_state=salobj.State.STANDBY,
            config_dir=TEST_CONFIG_DIR,
            simulation_mode=1,
        ):
            await self.check_standard_state_transitions(enabled_commands=[])

    async def test_telemetry_publishing(self):
        async with self.make_csc(
            initial_state=salobj.State.STANDBY,
            config_dir=TEST_CONFIG_DIR,
            simulation_mode=1,
        ):
            await salobj.set_summary_state(
                self.remote, salobj.State.ENABLED,
                settingsToApply="pytest_config.yaml"
            )
            await self.assert_next_sample(
                pressure_ch1=-10,
                pressure_ch2=10,
                topic=self.remote.tel_pressure,
                flush=True
            )

            # check that our near-zero values are near-zero
            data = await self.assert_next_sample(
                topic=self.remote.tel_pressure,
                flush=True
            )
            self.assertAlmostEqual(data.pressure_ch3, 0, places=3)
            self.assertAlmostEqual(data.pressure_ch4, 0, places=3)

    async def test_dynamic_fake_telemetry(self):
        """
        Make sure channels 0 and 5 are pressure and temperature,
        respectively, and that they are changing over time.
        """
        async with self.make_csc(
            initial_state=salobj.State.STANDBY,
            config_dir=TEST_CONFIG_DIR,
            simulation_mode=1,
        ):
            await salobj.set_summary_state(
                self.remote, salobj.State.ENABLED,
                settingsToApply="pytest_config.yaml"
            )

            pressure_data1 = await self.assert_next_sample(
                topic=self.remote.tel_pressure,
                flush=True
            )
            temp_data1 = await self.assert_next_sample(
                topic=self.remote.tel_temperature,
                flush=True
            )
            await asyncio.sleep(2)
            pressure_data2 = await self.assert_next_sample(
                topic=self.remote.tel_pressure,
                flush=True
            )
            temp_data2 = await self.assert_next_sample(
                topic=self.remote.tel_temperature,
                flush=True
            )

            self.assertNotEqual(pressure_data1.pressure_ch0, pressure_data2.pressure_ch0)
            self.assertNotEqual(temp_data1.temp_ch5, temp_data2.temp_ch5)

    async def test_bad_sensor_type(self):
        async with self.make_csc(
            initial_state=salobj.State.STANDBY,
            config_dir=TEST_CONFIG_DIR,
            simulation_mode=1,
        ):
            with self.assertRaises(RuntimeError):
                await salobj.set_summary_state(
                    self.remote, salobj.State.ENABLED,
                    settingsToApply="malformed_config.yaml"
                )


if __name__ == "__main__":
    unittest.main()
