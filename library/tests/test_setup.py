import ina220


def test_setup(smbus):
    """Mock the presence of a INA220 and test initialisation."""
    sensor = ina220.INA220()  # noqa F841


def test_shunt_voltage(smbus):
    sensor = ina220.INA220()
    assert sensor.get_shunt_voltage_measurement().reading == 64


def test_bus_voltage(smbus):
    sensor = ina220.INA220()
    assert sensor.get_bus_voltage_measurement().reading == 2048


def test_get_measurements(smbus):
    sensor = ina220.INA220()
    assert [int(x) for x in sensor.get_measurements()] == [546, 8, 0]
