import unittest
import asyncio
import pytest
from lsst.ts import adamSensors


class ModelTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_connect(self):
        m = adamSensors.AdamModel("fakeIP", 502, simulation_mode=True)
        assert m is not None

    async def test_read_voltage(self):
        m = adamSensors.AdamModel("fakeIP", 502, simulation_mode=True)
        v1 = await m.read_voltage()

        # check the min, max, and zero-ish values from simulator
        assert v1[1] == pytest.approx(-10)
        assert v1[2] == pytest.approx(10)
        assert v1[3] == pytest.approx(0, abs=1e-3)
        assert v1[4] == pytest.approx(0, abs=1e-3)

        # check that channel 0 is changing over time
        await asyncio.sleep(2)
        v2 = await m.read_voltage()
        assert v1[0] != v2[0]


if __name__ == "__main__":
    unittest.main()
