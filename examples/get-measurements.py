#!/usr/bin/env python3

from ina220 import INA220
import time


ina220 = INA220()


ina220.set_bus_voltage_range(0)
ina220._ina220.set('CONFIG', mode='shunt_and_bus_continuous')

while (1):
    current, voltage, voltage_across_shunt = ina220.get_measurements()
    print("Current: {0:.2f}A Voltage: {1:.2f}V Shunt Voltage: {2:.5f}V".format(current, voltage, voltage_across_shunt))
    time.sleep(1)
