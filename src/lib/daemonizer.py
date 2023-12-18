import os
import subprocess
import sys
import textwrap

from definitions import ROOT_DIR


class Daemonizer:
    _SERVICE_FILE = "/etc/systemd/system/{service_name}.service"
    _SERVICE_FILE_CONTENT = textwrap.dedent(
        """[Unit]
        Description={service_description}

        [Service]
        WorkingDirectory={working_directory}
        ExecStart={exec_start}
        User={user}
        Type=simple
        Restart=always

        [Install]
        WantedBy=multi-user.target"""
    )

    def __init__(
        self,
        python_module_name=None,
        service_name=None,
        service_description="No description provided",
    ):
        self._python_module_name = python_module_name
        self._service_name = service_name
        self._service_file = self._SERVICE_FILE.format(service_name=self._service_name)
        self._service_description = service_description

        if self._python_module_name is None or self._service_name is None:
            raise ValueError(
                "python_module_name and service_name are required arguments"
            )

    def daemonize(self):
        if self._is_service_installed() and self._is_service_running():
            print(f"The {self._service_name} service is already running.")
        else:
            self._install_service()
            self._start_service()
            print(f"The {self._service_name} service has been installed and started.")

    def _install_service(self):
        service_file_content = self._generate_service_file_content()
        self._write_service_file_content(service_file_content)

    def _start_service(self):
        subprocess.run(["sudo", "systemctl", "daemon-reload"])
        subprocess.run(["sudo", "systemctl", "enable", self._service_name])
        subprocess.run(["sudo", "systemctl", "start", self._service_name])

    def _generate_service_file_content(self):
        pipenv_path = self._get_pipenv_path()

        exec_start = f"{pipenv_path} run python -m {self._python_module_name}"
        working_directory = ROOT_DIR
        user = os.getenv("USER")

        service_file_content = self._SERVICE_FILE_CONTENT.format(
            service_description=self._service_description,
            exec_start=exec_start,
            working_directory=working_directory,
            user=user,
        )
        return service_file_content

    def _write_service_file_content(self, service_file_content):
        try:
            subprocess.run(
                ["sudo", "tee", self._service_file],
                input=service_file_content,
                stdout=subprocess.DEVNULL,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"Error writing to {self._service_file}: {e}")
            sys.exit(1)

    def _get_pipenv_path(self):
        try:
            result = subprocess.run(
                ["which", "pipenv"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
            )
            pipenv_path = result.stdout.strip()
            return pipenv_path
        except subprocess.CalledProcessError:
            print("pipenv not found")
            sys.exit(1)

    def _is_service_installed(self):
        return os.path.exists(self._service_file)

    def _is_service_running(self):
        try:
            subprocess.check_output(
                ["systemctl", "is-active", "--quiet", self._service_name]
            )
            return True
        except subprocess.CalledProcessError:
            return False
        except subprocess.CalledProcessError:
            return False
