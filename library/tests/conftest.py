import sys
import mock
import pytest


class MockSMBus:
    """Mock enough of the INA220 for the library to initialise and test."""

    def __init__(self, bus):
        """Initialise with test data."""
        self.regs = [0 for _ in range(256)]

        self.regs[0x01:0x02] = [0x00, 0x01]  # Shunt Voltage
        self.regs[0x03:0x04] = [0x00, 0x01]  # Bus Voltage

    def read_byte_data(self, addr, register):
        """Read a single byte from fake registers."""
        return self.regs[register]

    def write_byte_data(self, addr, register, value):
        """Write a single byte to fake registers."""
        self.regs[register] = value

    def read_i2c_block_data(self, addr, register, length):
        """Read up to length bytes from register."""
        return self.regs[register:register + length]


@pytest.fixture(scope='function', autouse=False)
def smbus():
    """Mock smbus module."""
    smbus = mock.MagicMock()
    smbus.SMBus = MockSMBus
    sys.modules['smbus'] = smbus
    yield smbus
    del sys.modules['smbus']
