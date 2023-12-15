import time
import schedule
from lib.models import Sht30Reading
from lib.sht30 import Sht30

sht30 = Sht30()

def record_sht30_reading():
    sensor_data = sht30.read()
    temperature = sensor_data['temperature']
    humidity = sensor_data['humidity']

    if temperature is not None and humidity is not None:
        Sht30Reading.create(temperature=temperature, humidity=humidity)
        print(f"Recorded: Temperature={temperature:.2f}°C, Humidity={humidity:.2f}%")
    else:
        print("Failed to read sensor data.")

schedule.every(3).seconds.do(record_sht30_reading)

while True:
    schedule.run_pending()
    time.sleep(1)
