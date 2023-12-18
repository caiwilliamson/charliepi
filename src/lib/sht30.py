import smbus


class Sht30:
    def __init__(self):
        self._bus = smbus.SMBus(1)

    def read(self):
        self._bus.write_i2c_block_data(0x44, 0x2C, [0x06])
        data = self._bus.read_i2c_block_data(0x44, 0x00, 6)
        cTemp = ((((data[0] * 256.0) + data[1]) * 175) / 65535.0) - 45
        humidity = 100 * (data[3] * 256 + data[4]) / 65535.0
        return {"temperature": round(cTemp, 2), "humidity": round(humidity, 2)}
