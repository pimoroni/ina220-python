import ina220


def test_setup(smbus):
    """Mock the presence of a INA220 and test initialisation."""
    sensor = ina220.INA220()  # noqa F841


def test_shunt_voltage(smbus):
    sensor = ina220.INA220()
    assert sensor.get_shunt_voltage() == 0.04095


def test_bus_voltage(smbus):
    sensor = ina220.INA220()
    assert sensor.get_bus_voltage() == 32.644


def test_get_measurements(smbus):
    sensor = ina220.INA220()
    assert [int(x) for x in sensor.get_measurements()] == [8, 32, 0]
