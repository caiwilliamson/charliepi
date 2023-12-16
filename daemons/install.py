import os
import sys
import subprocess

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from definitions import ROOT_DIR

SERVICE_NAME = "sht30_recorder"
SERVICE_FILE = f"/etc/systemd/system/{SERVICE_NAME}.service"

def is_service_installed():
    return os.path.exists(SERVICE_FILE)

def is_service_running():
    try:
        subprocess.check_output(["systemctl", "is-active", "--quiet", SERVICE_NAME])
        return True
    except subprocess.CalledProcessError:
        return False

def get_pipenv_path():
    try:
        result = subprocess.run(
            ['which', 'pipenv'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        pipenv_path = result.stdout.strip()
        return pipenv_path
    except subprocess.CalledProcessError:
        print("pipenv not found")
        sys.exit(1)

def read_service_file_template_content():
    script_location = os.path.abspath(os.path.dirname(__file__))
    service_file_path = os.path.join(script_location, f"{SERVICE_NAME}.service")

    with open(service_file_path, "r") as template_file:
        template_content = template_file.read()

    return template_content

def generate_service_file_content():
    pipenv_path = get_pipenv_path()

    template_content = read_service_file_template_content()
    exec_start = f"{pipenv_path} run python daemons/{SERVICE_NAME}.py"
    working_directory = ROOT_DIR
    user = os.getenv('USER')

    service_file_content = (
        template_content
        .replace("{{EXEC_START}}", exec_start)
        .replace("{{WORKING_DIRECTORY}}", working_directory)
        .replace("{{USER}}", user)
    )
    return service_file_content

def write_service_file_content(service_file_content):
    try:
        subprocess.run(
            ['sudo', 'tee', SERVICE_FILE],
            input=service_file_content,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error writing to {SERVICE_FILE}: {e}")
        sys.exit(1)

def install_service():
    service_file_content = generate_service_file_content()
    write_service_file_content(service_file_content)

def start_service():
    subprocess.run(["sudo", "systemctl", "daemon-reload"])
    subprocess.run(["sudo", "systemctl", "enable", SERVICE_NAME])
    subprocess.run(["sudo", "systemctl", "start", SERVICE_NAME])

def install_and_start_service():
    install_service()
    start_service()

if __name__ == "__main__":
    if is_service_installed() and is_service_running():
        print(f"The {SERVICE_NAME} service is already running.")
    else:
        install_and_start_service()
        print(f"The {SERVICE_NAME} service has been installed and started.")
