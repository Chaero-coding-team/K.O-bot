from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Challenge:
    opponent: str

    board_size: int = 19
    speed: str = ""
    rules: str = "japanese"

    handicap: int = 0

    ranked: bool = True
    private: bool = False

    # OGS에서 전달되는 게임 타입
    game_type: str = "game"


class ChallengeFilter:

    def __init__(self):
        self.mode = os.getenv(
            "MODE",
            "learning"
        ).lower()

        self.teacher_username = os.getenv(
            "TEACHER_USERNAME",
            ""
        ).strip()

        self.allowed_board_size = 19

        # 네가 허용한다고 한 시간 형태
        self.allowed_speeds = {
            "blitz",
            "correspondence",
        }

    def check(self, challenge: Challenge) -> tuple[bool, str]:

        # --------------------------------------------------
        # 1. 19x19만
        # --------------------------------------------------

        if challenge.board_size != self.allowed_board_size:
            return (
                False,
                "19x19가 아님"
            )

        # --------------------------------------------------
        # 2. 시간 형식
        # --------------------------------------------------

        speed = challenge.speed.lower()

        if speed not in self.allowed_speeds:
            return (
                False,
                f"허용하지 않는 시간 형식: {speed}"
            )

        # --------------------------------------------------
        # 3. 룰
        # --------------------------------------------------

        rules = challenge.rules.lower()

        korean_rules = {
            "korean",
            "korean rules",
            "korean_rule",
        }

        if rules not in korean_rules:
            return (
                False,
                f"한국식 룰이 아님: {rules}"
            )

        # --------------------------------------------------
        # 4. 학습 모드
        # --------------------------------------------------

        if self.mode == "learning":

            if (
                not self.teacher_username
                or challenge.opponent.lower()
                != self.teacher_username.lower()
            ):
                return (
                    False,
                    "학습 모드에서는 선생님만 허용"
                )

            # 학습 모드에서 핸디캡 금지
            if challenge.handicap != 0:
                return (
                    False,
                    "학습 모드에서는 핸디캡을 허용하지 않음"
                )

        # --------------------------------------------------
        # 5. 일반 모드
        # --------------------------------------------------

        elif self.mode == "normal":

            # 일반 모드에서는 핸디캡 자체는 허용하되
            # 친선전인지 확인
            if challenge.handicap > 0:

                if challenge.ranked:
                    return (
                        False,
                        "랭크전 핸디캡은 허용하지 않음"
                    )

        else:

            return (
                False,
                f"알 수 없는 MODE: {self.mode}"
            )

        # --------------------------------------------------
        # 6. 승인
        # --------------------------------------------------

        return (
            True,
            "모든 조건 만족"
        )

    def describe(self, challenge: Challenge):

        print()
        print("=" * 50)
        print("새로운 대국 신청")
        print("=" * 50)

        print(
            f"상대: {challenge.opponent}"
        )

        print(
            f"판 크기: {challenge.board_size}x"
            f"{challenge.board_size}"
        )

        print(
            f"시간: {challenge.speed}"
        )

        print(
            f"룰: {challenge.rules}"
        )

        print(
            f"핸디캡: {challenge.handicap}"
        )

        print(
            f"랭크전: {challenge.ranked}"
        )

        print(
            f"모드: {self.mode}"
        )

        accepted, reason = self.check(
            challenge
        )

        print("-" * 50)

        if accepted:
            print(
                "결과: ACCEPT"
            )
        else:
            print(
                "결과: REJECT"
            )

        print(
            f"이유: {reason}"
        )

        print("=" * 50)

        return accepted
