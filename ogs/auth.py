from __future__ import annotations

import logging
import os
import time

import requests
from dotenv import load_dotenv


load_dotenv()

logger = logging.getLogger(__name__)

OGS_BASE_URL = "https://online-go.com"


class OGSAuth:
    def __init__(self):
        self.client_id = os.getenv("OGS_CLIENT_ID")
        self.client_secret = os.getenv("OGS_CLIENT_SECRET")

        self.username = os.getenv("OGS_USERNAME")
        self.password = os.getenv("OGS_PASSWORD")

        self.access_token = None
        self.refresh_token = None
        self.user_jwt = None

        self.expires_at = 0

        self._validate_config()

    def _validate_config(self):
        required = {
            "OGS_CLIENT_ID": self.client_id,
            "OGS_CLIENT_SECRET": self.client_secret,
            "OGS_USERNAME": self.username,
            "OGS_PASSWORD": self.password,
        }

        missing = [
            name
            for name, value in required.items()
            if not value
        ]

        if missing:
            raise RuntimeError(
                "다음 환경변수가 없습니다: "
                + ", ".join(missing)
            )

    def login(self):
        """
        OGS OAuth password grant 로그인.
        """

        logger.info("OGS OAuth 로그인 시작...")

        data = {
            "grant_type": "password",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "username": self.username,
            "password": self.password,
        }

        response = requests.post(
            f"{OGS_BASE_URL}/oauth2/token/",
            data=data,
            timeout=20,
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"OGS OAuth 로그인 실패: "
                f"{response.status_code} "
                f"{response.text}"
            )

        token = response.json()

        self.access_token = token.get("access_token")
        self.refresh_token = token.get("refresh_token")

        expires_in = int(
            token.get("expires_in", 0)
        )

        self.expires_at = (
            time.time() + expires_in
        )

        if not self.access_token:
            raise RuntimeError(
                "OGS가 access_token을 반환하지 않았습니다."
            )

        logger.info(
            "OGS OAuth 로그인 성공"
        )

        # OGS UI config에서 realtime 인증 정보를 가져온다.
        self._load_auth_config()

        return self.access_token

    def _load_auth_config(self):
        response = requests.get(
            f"{OGS_BASE_URL}/api/v1/ui/config/",
            headers={
                "Authorization":
                    f"Bearer {self.access_token}",
                "Content-Type": "application/json",
            },
            timeout=20,
        )

        if response.status_code != 200:
            raise RuntimeError(
                "OGS auth config 요청 실패: "
                f"{response.status_code} "
                f"{response.text}"
            )

        config = response.json()

        # OGS realtime authentication 정보
        self.user_jwt = (
            config.get("user_jwt")
        )

        if not self.user_jwt:
            raise RuntimeError(
                "OGS config에서 user_jwt를 찾지 못했습니다."
            )

        logger.info(
            "Realtime JWT 획득 성공"
        )

    def get_access_token(self):
        if not self.access_token:
            self.login()

        return self.access_token

