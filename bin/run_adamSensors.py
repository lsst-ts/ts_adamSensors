#!/usr/bin/env python
import asyncio
from lsst.ts import adamSensors

asyncio.run(adamSensors.AdamCSC.amain(index=None))
