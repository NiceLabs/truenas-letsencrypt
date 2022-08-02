#!/usr/bin/env python3
from api import TrueNASCertificateClient

import urllib3.exceptions

urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)


def main():
    client = TrueNASCertificateClient(
        api_key="1-H3NPlBgX9DyLjGkKFQ09HZXEvcIPK6kLVmabcBqk7bMbAeYnxorWOvlRxLgkK6lQ",
        base_url="https://192.168.1.130",
    )
    client.session.verify = False
    client.ping()
    print(client.used_certificates())


if __name__ == "__main__":
    main()
