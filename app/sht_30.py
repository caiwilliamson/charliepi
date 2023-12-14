import smbus
import time

def read_sht_30():
    bus = smbus.SMBus(1)
    bus.write_i2c_block_data(0x44, 0x2C, [0x06])
    data = bus.read_i2c_block_data(0x44, 0x00, 6)
    cTemp = ((((data[0] * 256.0) + data[1]) * 175) / 65535.0) - 45
    humidity = 100 * (data[3] * 256 + data[4]) / 65535.0
    return {'temperature': round(cTemp, 2), 'humidity': round(humidity, 2)}
