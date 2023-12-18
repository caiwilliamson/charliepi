import logging

import requests
from dotenv import dotenv_values
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from src.lib.setup_logging import setup_logging

requests.packages.urllib3.util.connection.HAS_IPV6 = False

setup_logging("healthchecks")


class HealthchecksMissingPingKeyError(Exception):
    pass


class HealthchecksMissingSlugError(Exception):
    pass


class HealthchecksPinger:
    PING_DOMAIN = "https://hc-ping.com"
    MISSING_SLUG_ERROR = "Can't ping Healthchecks because slug is not defined"
    MISSING_PING_KEY_ERROR = "Can't ping Healthchecks because HEALTHCHECKS_PING_KEY is missing from the environment!"

    def __init__(self, slug=None):
        config = dotenv_values(".env")

        self._slug = slug
        self._ping_key = config.get("HEALTHCHECKS_PING_KEY", None)
        self._http_session = None

        if self._slug is None:
            logging.error(self.MISSING_SLUG_ERROR)
            raise HealthchecksMissingSlugError(self.MISSING_SLUG_ERROR)

        if self._ping_key is None:
            logging.error(self.MISSING_PING_KEY_ERROR)
            raise HealthchecksMissingPingKeyError(self.MISSING_PING_KEY_ERROR)

    def ping(self):
        url = f"{self.PING_DOMAIN}/{self._ping_key}/{self._slug}"
        http_session = self._create_http_session()

        try:
            response = http_session.get(url, timeout=10)
            logging.info(f"Pinged Healthchecks. Response: {response.text}")
        except requests.RequestException as e:
            logging.error(f"Failed to ping Healthchecks.io: {e}")

    def _create_http_session(self):
        if self._http_session is None:
            retries = Retry(total=5, backoff_factor=0.1)
            adapter = HTTPAdapter(max_retries=retries)
            http_session = requests.Session()
            http_session.mount("https://", adapter)
            self._http_session = http_session

        return self._http_session
