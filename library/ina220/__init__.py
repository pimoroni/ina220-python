import time
from i2cdevice import Device, Register, BitField
from i2cdevice.adapter import Adapter, LookupAdapter


__version__ = '0.0.1'


class SensorDataAdapter(Adapter):
    """Convert from 16-bit sensor data with crazy offset"""
    def __init__(self, bit_resolution=14):
        self.bit_resolution = bit_resolution

    def _encode(self, value):
        return value

    def _decode(self, value):
        LSB = (value & 0xFF00) >> 10
        MSB = (value & 0x00FF) << 6
        # print (bin(MSB),bin(LSB))
        return MSB + LSB


class ina220config:
    def __init__(self):
        self.bus_voltage_range = 0b0
        self.pga_gain = '0' 
        self.bus_adc_setting = ''
        self.shunt_adc_setting =''
        self.mode = ''


class INA220:
    def __init__(self, i2c_addr=0x45, i2c_dev=None):
        self._i2c_addr = i2c_addr
        self._i2c_dev = i2c_dev
        self._is_setup = False

        self._configuration = ina220config()

        self._ina220 = Device([0x45], i2c_dev=self._i2c_dev, bit_width=16, registers=(
            Register('CONFIG', 0x00, fields=(
                BitField('reset', 0b1000000000000000),
                BitField('bus_voltage_range', 0b0010000000000000),
                BitField('pga_gain', 0b0001100000000000, adapter=LookupAdapter({
                    '40': 0b00,
                    '80': 0b01,
                    '160': 0b10,
                    '320': 0b11
                })),
                BitField('bus_adc', 0b0000011110000000, adapter=LookupAdapter({
                    '9bit': 0b0000,
                    '10bit': 0b0001,
                    '11bit': 0b0010,
                    '12bit': 0b0011,
                    '2samples': 0b1001,
                    '4samples': 0b1010,
                    '8samples': 0b1011,
                    '16samples': 0b1100,
                    '32samples': 0b1101,
                    '64samples': 0b1110,
                    '128samples': 0b1111
                })),
                BitField('shunt_adc', 0b0000000001111000, adapter=LookupAdapter({
                    '9bit': 0b0000,
                    '10bit': 0b0001,
                    '11bit': 0b0010,
                    '12bit': 0b0011,
                    '2samples': 0b1001,
                    '4samples': 0b1010,
                    '8samples': 0b1011,
                    '16samples': 0b1100,
                    '32samples': 0b1101,
                    '64samples': 0b1110,
                    '128samples': 0b1111
                })),
                BitField('mode', 0b0000000000000111, adapter=LookupAdapter({
                    'power_down': 0b000,
                    'shunt_voltage_triggered': 0b001,
                    'bus_voltage_triggered': 0b010,
                    'shunt_and_bus_triggered': 0b011,
                    'adc_off': 0b100,
                    'shunt_voltage_continuous': 0b101,
                    'bus_voltage_continuous': 0b110,
                    'shunt_and_bus_continuous': 0b111
                })),

            )),

            Register('SHUNT_VOLTAGE', 0x01, fields=(
                BitField('reading',0xFFFF , adapter=SensorDataAdapter()),
            ), bit_width=16, read_only=True),
            
            Register('BUS_VOLTAGE', 0x02, fields=(
                BitField('reading', 0b1111111111111000, adapter=SensorDataAdapter()),
                BitField('conversion_ready', 0b0000000000000010),
                BitField('math_overflow_flag', 0b0000000000000001)

            ), bit_width=16, read_only=True),

            Register('POWER', 0x03, fields=(
                BitField('reading', 0xFFFF, adapter=SensorDataAdapter()),
            ), bit_width=16, read_only=True),

            Register('CURRENT', 0x04, fields=(
                BitField('reading', 0xFFFF, adapter=SensorDataAdapter()),
            ), bit_width=16, read_only=True),

            Register('CALIBARTION', 0x05, fields=(
                BitField('reading', 0xFFFF, adapter=SensorDataAdapter()),
            ), bit_width=16, read_only=True),
        ))

        self.get_configuration()

    def get_configuration(self):
        self._configuration.bus_voltage_range = self._ina220.CONFIG.get_bus_voltage_range()
        self._configuration.pga_gain = self._ina220.CONFIG.get_pga_gain()
        self._configuration.bus_adc_setting = self._ina220.CONFIG.get_bus_adc()
        self._configuration.shunt_adc_setting = self._ina220.CONFIG.get_shunt_adc()
        self._configuration.mode = self._ina220.CONFIG.get_mode()
        return self._configuration

    def set_bus_voltage_range(self, bus_voltage_range):
        self._ina220.CONFIG.set_bus_voltage_range(bus_voltage_range)


if __name__ == "__main__":
    import smbus

    bus = smbus.SMBus(1)
    pmic = INA220(i2c_dev=bus)


