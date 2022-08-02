from datetime import datetime, timedelta
from typing import Set
from urllib.parse import urljoin
import os

import requests


class TrueNASCertificateClient:
    session = requests.Session()
    base_url: str

    def __init__(
        self,
        api_key: str,
        base_url="https://localhost",
    ):
        self.base_url = urljoin(base_url, "/api/v2.0/")
        self.session.headers["content-type"] = "application/json"
        self.session.headers["authorization"] = f"Bearer {api_key}"

    def api(self, url: str):
        return urljoin(self.base_url, url)

    def ping(self, timeout=100):
        return self.session.get(self.api("core/ping"), timeout=timeout)

    def create(self, name: str, full_chain: str, private_key: str):
        response = self.session.post(
            self.api("certificate"),
            data={
                "create_type": "CERTIFICATE_CREATE_IMPORTED",
                "name": name,
                "certificate": full_chain,
                "privatekey": private_key,
            },
        )
        if not response.ok:
            response.raise_for_status()
        return response.json()

    def list(self, limit: int = 0):
        response = self.session.get(self.api("certificate"), params={"limit": limit})
        if not response.ok:
            response.raise_for_status()
        return response.json()

    def delete(self, certificate_id: int):
        response = self.session.delete(self.api(f"certificate/id/{certificate_id}"))
        if not response.ok:
            response.raise_for_status()
        return response.json()

    def get_ui_certificate(self) -> int:
        response = self.session.get(self.api("system/general"))
        if not response.ok:
            response.raise_for_status()
        return response.json().get("ui_certificate")

    def set_ui_certificate_id(self, certificate_id: int):
        response = self.session.put(
            self.api("system/general"),
            data={"ui_certificate": certificate_id},
        )
        if not response.ok:
            response.raise_for_status()
        return response.json()

    def get_service_certificate(self, service_name: str) -> int:
        response = self.session.get(self.api(service_name))
        if not response.ok:
            response.raise_for_status()
        return response.json().get("certificate")

    def set_service_certificate_id(self, service_name: str, certificate_id: int):
        if service_name == "console":
            service_name = "system/general"
        response = self.session.put(
            self.api(service_name),
            data={"certificate": certificate_id},
        )
        if not response.ok:
            response.raise_for_status()
        return response.json()

    def restart(self, service_name: str):
        if service_name == "console":
            return self.session.post(self.api("system/general/ui_restart"))
        response = self.session.post(
            self.api("service/restart"),
            data={"service": service_name},
        )
        if not response.ok:
            response.raise_for_status()
        return response.json()

    def used_certificates(self):
        return {
            "ui": self.get_ui_certificate(),
            "s3": self.get_service_certificate("s3"),
            "ftp": self.get_service_certificate("ftp"),
            "webdav": self.get_service_certificate("webdav"),
        }

    def need_delete_certificate_ids(
        self, new_cert_san: Set[str], now=datetime.now()
    ) -> Set[int]:
        certs = self.list()
        same_san: Set[int] = {
            certificate["id"]
            for certificate in certs
            if set(certificate["san"]) == new_cert_san
        }
        expired: Set[int] = {
            c["id"]
            for c in certs
            if now > datetime.strptime(c["from"], "%c") + timedelta(days=c["lifetime"])
        }
        return same_san | expired


def import_letsencrypt(
    client: TrueNASCertificateClient,
    certificate_name: str,
    letsencrypt_name: str,
    base_path="/etc/letsencrypt/live",
):
    def read(pathname: str):
        with open(os.path.join(base_path, letsencrypt_name, pathname), "r") as fp:
            return fp.read()

    return client.create(certificate_name, read("fullchain.pem"), read("privkey.pem"))
