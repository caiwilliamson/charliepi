from src.lib.daemonize import Daemonize

if __name__ == "__main__":
    Daemonize(
        python_module_name="src.sht30_recorder",
        service_name="sht30_recorder",
        service_description="Record temperature and humidity readings from SHT30 sensor",
    )
    Daemonize(
        python_module_name="src.web_app",
        service_name="web_app",
        service_description="Charlie Pi web application",
    )
