import os
import sys
import inspect
import subprocess
from definitions import ROOT_DIR

class Daemonize:
    SERVICE_FILE = "/etc/systemd/system/{service_name}.service"
    SERVICE_FILE_CONTENT = """[Unit]
Description={service_description}

[Service]
WorkingDirectory={working_directory}
ExecStart={exec_start}
User={user}
Type=simple
Restart=always

[Install]
WantedBy=multi-user.target"""

    def __init__(
        self,
        python_module_name=None,
        service_name=None,
        service_description="No description provided"
    ):
        self.python_module_name = python_module_name
        self.service_name = service_name
        self.service_file = self.SERVICE_FILE.format(service_name=self.service_name)
        self.service_description = service_description

        if self.python_module_name is None or self.service_name is None:
            raise ValueError("python_module_name and service_name are required arguments")

        self.daemonize()

    def is_service_installed(self):
        return os.path.exists(self.service_file)

    def is_service_running(self):
        try:
            subprocess.check_output(["systemctl", "is-active", "--quiet", self.service_name])
            return True
        except subprocess.CalledProcessError:
            return False

    def get_pipenv_path(self):
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

    def generate_service_file_content(self):
        pipenv_path = self.get_pipenv_path()

        exec_start = f"{pipenv_path} run python -m {self.python_module_name}"
        working_directory = ROOT_DIR
        user = os.getenv('USER')

        service_file_content = Daemonize.SERVICE_FILE_CONTENT.format(
            service_description=self.service_description,
            exec_start=exec_start,
            working_directory=working_directory,
            user=user
        )
        return service_file_content

    def write_service_file_content(self, service_file_content):
        try:
            subprocess.run(
                ['sudo', 'tee', self.service_file],
                input=service_file_content,
                stdout=subprocess.DEVNULL,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"Error writing to {self.service_file}: {e}")
            sys.exit(1)

    def install_service(self):
        service_file_content = self.generate_service_file_content()
        self.write_service_file_content(service_file_content)

    def start_service(self):
        subprocess.run(["sudo", "systemctl", "daemon-reload"])
        subprocess.run(["sudo", "systemctl", "enable", self.service_name])
        subprocess.run(["sudo", "systemctl", "start", self.service_name])

    def install_and_start_service(self):
        self.install_service()
        self.start_service()

    def daemonize(self):
        if self.is_service_installed() and self.is_service_running():
            print(f"The {self.service_name} service is already running.")
        else:
            self.install_and_start_service()
            print(f"The {self.service_name} service has been installed and started.")
