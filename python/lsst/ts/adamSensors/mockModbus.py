from time import time
from math import sin
from collections import namedtuple


class MockModbusClient:
    def __init__(self, client, port):
        pass

    async def read_input_registers(self, address, count=1, unit=1):
        """
        Mock version of pymodbus class that reads voltages
        off of the ADAM 6024's analog inputs. The first and
        last ones are sinusoids with different periods, the rest
        are static. 0 and 65535 represent the minimum and maximum
        values we ever expect to see from the ADAM 6024, which
        translate into -10 and +10 volts respectively.

        Parameters:
        -----------
        address: starting point of the range we want to read.
                 for the ADAM 6024, always zero.
        count:   number of sequential values to read from
                 the adam device.
        """

        Fake_readout = namedtuple("Fake_readout", ["registers"])
        return Fake_readout(
            registers=[self._sin(7), 0, 65535, 32767, 32768, self._sin(11)]
        )

    async def close(self):
        pass

    def _sin(self, period):
        return abs(sin(time() / period) * 65535)
