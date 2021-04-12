from setuptools import setup
setup(
    name="ts-adamSensors",
    packages=["lsst.ts.adamSensors"],
    version=1.0.0,
    install_requires['ts_salobj', 'pymodbus'],
)