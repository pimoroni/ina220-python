from ina220 import INA220
import time 
ina220 = INA220()

voltage = 0.0
current = 0.0 
voltage_across_shunt = 0.0



while (1):
    current, voltage, voltage_across_shunt = ina220.get_measurements(self)
    print("Current: {0} Voltage: {1} Shunt Voltage: {2}".fromat(current, voltage, voltage_across_shunt))
    time.sleep(1)