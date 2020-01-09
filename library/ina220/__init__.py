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


class ADCLookupAdapter(LookupAdapter):
    def _decode(self, value):
        # Mask out the "don't care" bit for anything
        # that doesn't have the high bit set
        if value & 0b1000 == 0:
            value &= 0b0011
        # Special case for 0b1000 = 12bit
        if value == 0b1000:
            value = 0b0011
        LookupAdapter._decode(self, value)


# This lookup adaptor applies to both the Bus ADC and Shunt ADC
# and has a lot of caveats for weird treatment of bits.
# Defining it once up here lets us enshrine how irritating it is!
sadc_badc_adapter = ADCLookupAdapter({
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
})


class INA220:
    def __init__(self, i2c_addr=0x45, i2c_dev=None):
        self._i2c_addr = i2c_addr
        self._i2c_dev = i2c_dev
        self._is_setup = False

        self._ina220 = Device([self._i2c_addr], i2c_dev=self._i2c_dev, bit_width=8, registers=(
            Register('CONFIG', 0x00, fields=(
                BitField('reset', 0b1000000000000000),
                BitField('bus_voltage_range', 0b0010000000000000),
                BitField('pga_gain', 0b0001100000000000, adapter=LookupAdapter({
                    '40': 0b00,
                    '80': 0b01,
                    '160': 0b10,
                    '320': 0b11
                }), bit_width=16),
                BitField('bus_adc', 0b0000011110000000, adapter=sadc_badc_adapter, bit_width=16),
                BitField('shunt_adc', 0b0000000001111000, adapter=sadc_badc_adapter, bit_width=16),
                BitField('mode', 0b0000000000000111, adapter=LookupAdapter({
                    'power_down': 0b000,
                    'shunt_voltage_triggered': 0b001,
                    'bus_voltage_triggered': 0b010,
                    'shunt_and_bus_triggered': 0b011,
                    'adc_off': 0b100,
                    'shunt_voltage_continuous': 0b101,
                    'bus_voltage_continuous': 0b110,
                    'shunt_and_bus_continuous': 0b111
                }), bit_width=16),

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

        self._configuration = self.get_configuration()

    def get_configuration(self):
        return self._ina220.get('CONFIG')

    def set_bus_voltage_range(self, bus_voltage_range):
        self._ina220.CONFIG.set_bus_voltage_range(bus_voltage_range)


if __name__ == "__main__":
    import smbus

    bus = smbus.SMBus(1)
    pmic = INA220(i2c_dev=bus)


