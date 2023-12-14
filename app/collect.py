import time
import schedule
from sensor_data import SensorData
from sht_30 import read_sht_30

def record_sensor_data():
    sensor_data = read_sht_30()
    temperature = sensor_data['temperature']
    humidity = sensor_data['humidity']

    if temperature is not None and humidity is not None:
        SensorData.create(temperature=temperature, humidity=humidity)
        print(f"Recorded: Temperature={temperature:.2f}°C, Humidity={humidity:.2f}%")
    else:
        print("Failed to read sensor data.")

schedule.every(3).seconds.do(record_sensor_data)

while True:
    schedule.run_pending()
    time.sleep(1)
