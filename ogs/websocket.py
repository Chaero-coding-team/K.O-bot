import json
import logging
import threading

import websocket


logger = logging.getLogger(__name__)


class OGSWebSocket:
    def __init__(self, url: str):
        self.url = url
        self.ws = None
        self.connected = False

    def on_open(self, ws):
        self.connected = True
        logger.info("OGS WebSocket 연결 성공")

    def on_message(self, ws, message):
        try:
            data = json.loads(message)

            logger.info(
                "OGS EVENT: %s",
                data
            )

        except json.JSONDecodeError:
            logger.warning(
                "JSON이 아닌 메시지를 받았습니다: %s",
                message
            )

    def on_error(self, ws, error):
        logger.error(
            "OGS WebSocket 오류: %s",
            error
        )

    def on_close(self, ws, close_status_code, close_msg):
        self.connected = False

        logger.info(
            "OGS WebSocket 종료: code=%s message=%s",
            close_status_code,
            close_msg
        )

    def connect(self):
        self.ws = websocket.WebSocketApp(
            self.url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )

        thread = threading.Thread(
            target=self.ws.run_forever,
            daemon=True,
        )

        thread.start()

        return thread

    def send(self, data):
        if not self.ws or not self.connected:
            raise RuntimeError("WebSocket이 연결되지 않았습니다.")

        message = json.dumps(data)

        self.ws.send(message)

    def close(self):
        if self.ws:
            self.ws.close()
