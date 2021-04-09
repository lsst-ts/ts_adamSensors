from time import time
from math import sin
from collections import namedtuple


class MockModbusClient:
    def __init__(self, client, port):
        pass

    async def read_input_registers(self, address, count=1, unit=1):
        """
        Mock version of pymodbus class that reads voltages
        off of the ADAM 6024's analog inputs. The first one
        is a sine wave based on time.time(), the rest are
        static. -10 and 10 represent the minimum and maximum
        values we ever expect to see from the ADAM 6024.

        Parameters:
        -----------
        address: starting point of the range we want to read.
                 for the ADAM 6024, always zero.
        count:   number of sequential values to read from
                 the adam device.
        """

        Fake_readout = namedtuple("Fake_readout", ["registers"])
        f = Fake_readout(registers=[sin(time() % 1 / 10) * 10, 0, -10, 10, -1.25, 3.14])

        return f

    async def close(self):
        pass
