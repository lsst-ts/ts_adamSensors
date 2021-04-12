from setuptools import setup
setup(
    name="ts-adamSensors",
    packages=["lsst.ts.adamSensors"],
    version=0.8,
    install_requires=['ts_salobj', 'pymodbus'],
)
