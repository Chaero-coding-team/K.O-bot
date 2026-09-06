from __future__ import annotations

import logging
import requests

import socketio

from .auth import OGSAuth


logger = logging.getLogger(__name__)

OGS_BASE_URL = "https://online-go.com"


class OGSClient:

    def __init__(self):
        self.auth = OGSAuth()

        self.user_id = None
        self.username = None

        self.sio = socketio.Client(
            logger=False,
            engineio_logger=False,
            reconnection=True,
        )

        self.connected = False

        self._register_events()

    def _register_events(self):

        @self.sio.event
        def connect():
            logger.info(
                "OGS Socket.IO 연결 성공"
            )

            self.connected = True

            # OGS Realtime 인증
            self.sio.emit(
                "authenticate",
                {
                    "jwt": self.auth.user_jwt
                }
            )

            logger.info(
                "OGS Realtime 인증 요청 전송"
            )

        @self.sio.event
        def disconnect():
            self.connected = False

            logger.warning(
                "OGS Socket.IO 연결 종료"
            )

        @self.sio.event
        def connect_error(data):
            logger.error(
                "OGS Socket.IO 연결 오류: %s",
                data
            )

        @self.sio.on("*")
        def catch_all(event, data):
            logger.info(
                "OGS EVENT: %s -> %s",
                event,
                data
            )

    def authenticate_account(self):
        logger.info(
            "OGS 계정 확인 중..."
        )

        token = self.auth.get_access_token()

        response = requests.get(
            f"{OGS_BASE_URL}/api/v1/me",
            headers={
                "Authorization":
                    f"Bearer {token}",
                "Content-Type": "application/json",
            },
            timeout=20,
        )

        if response.status_code != 200:
            raise RuntimeError(
                "OGS 계정 확인 실패: "
                f"{response.status_code} "
                f"{response.text}"
            )

        user = response.json()

        self.user_id = user.get("id")
        self.username = user.get("username")

        if not self.user_id:
            raise RuntimeError(
                "OGS 사용자 ID를 가져오지 못했습니다."
            )

        logger.info(
            "OGS 계정 확인 성공"
        )

        logger.info(
            "Username: %s",
            self.username
        )

        logger.info(
            "User ID: %s",
            self.user_id
        )

    def connect(self):

        # OAuth
        self.auth.login()

        # 계정 확인
        self.authenticate_account()

        logger.info(
            "OGS Realtime 서버 연결 중..."
        )

        self.sio.connect(
            OGS_BASE_URL,
            transports=["websocket"],
        )

        logger.info(
            "OGS Realtime 연결 완료"
        )

    def wait(self):
        self.sio.wait()

    def disconnect(self):

        if self.sio.connected:
            self.sio.disconnect()

        self.connected = False

        logger.info(
            "OGS 연결 종료"
        )
