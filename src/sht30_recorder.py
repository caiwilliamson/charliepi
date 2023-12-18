import time
import schedule
import threading
from src.lib.sht30 import Sht30
from src.lib.models import Sht30Reading
from src.lib.healthchecks_pinger import HealthchecksPinger

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

def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()

if __name__ == '__main__':
    healthchecks_pinger = HealthchecksPinger(slug="sht30-recorder")

    schedule.every(2).minutes.at(":00").do(run_threaded, healthchecks_pinger.ping)
    schedule.every().minute.at(":00").do(run_threaded, record_sht30_reading)

    while True:
        schedule.run_pending()
        time.sleep(1)
