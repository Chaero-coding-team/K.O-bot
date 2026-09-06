from __future__ import annotations

import logging
import os
import signal
import time

from dotenv import load_dotenv

from go_engine import GoEngine
from ogs.client import OGSClient


load_dotenv()


BOT_NAME = os.getenv(
    "BOT_NAME",
    "MyBot"
)

MODE = os.getenv(
    "MODE",
    "learning"
)

TEACHER_USERNAME = os.getenv(
    "TEACHER_USERNAME",
    ""
)


running = True


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


def shutdown(signum, frame):
    global running

    logger.info(
        "종료 요청을 받았습니다."
    )

    running = False


signal.signal(
    signal.SIGINT,
    shutdown
)

signal.signal(
    signal.SIGTERM,
    shutdown
)


def print_config():

    logger.info(
        "----------------------------------------"
    )

    logger.info(
        " OGS GO BOT - STAGE 3"
    )

    logger.info(
        "----------------------------------------"
    )

    logger.info(
        "Bot       : %s",
        BOT_NAME
    )

    logger.info(
        "Mode      : %s",
        MODE
    )

    logger.info(
        "Teacher   : %s",
        TEACHER_USERNAME or "(없음)"
    )

    logger.info(
        "Board     : 19x19"
    )

    logger.info(
        "Rules     : Korean"
    )

    logger.info(
        "----------------------------------------"
    )


def test_engine():

    logger.info(
        "자체 바둑 엔진 확인..."
    )

    engine = GoEngine()

    move = engine.play_our_move()

    if move:
        logger.info(
            "Engine test move: %s",
            move.gtp
        )

    logger.info(
        "엔진 확인 완료"
    )


def main():

    print_config()

    test_engine()

    client = None

    try:

        logger.info(
            "OGS client 생성..."
        )

        client = OGSClient()

        logger.info(
            "OGS 연결 시작..."
        )

        client.connect()

        logger.info(
            "========================================"
        )

        logger.info(
            " OGS 연결 성공!"
        )

        logger.info(
            " Bot: %s",
            client.username
        )

        logger.info(
            " User ID: %s",
            client.user_id
        )

        logger.info(
            "========================================"
        )

        logger.info(
            "현재 3단계에서는 대국을 자동 수락하지 않습니다."
        )

        logger.info(
            "OGS 이벤트를 기다리는 중..."
        )

        while running:

            time.sleep(1)

    except KeyboardInterrupt:

        logger.info(
            "KeyboardInterrupt"
        )

    except Exception as exc:

        logger.exception(
            "OGS 연결 중 오류 발생: %s",
            exc
        )

    finally:

        if client:
            client.disconnect()

        logger.info(
            "봇 종료"
        )


if __name__ == "__main__":
    main()



