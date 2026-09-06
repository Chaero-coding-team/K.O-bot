from challenge_filter import (
    Challenge,
    ChallengeFilter,
)


def test(name, challenge):

    checker = ChallengeFilter()

    accepted = checker.describe(
        challenge
    )

    print(
        f"\n{name}: "
        f"{'PASS' if accepted else 'REJECT'}"
    )


# 선생님 + 19x19 + 속기 + 한국식
test(
    "정상적인 학습 대국",
    Challenge(
        opponent="teacher_K.O bot",
        board_size=19,
        speed="blitz",
        rules="korean",
        handicap=0,
        ranked=True,
    ),
)


# 일반 사용자가 학습 모드에서 신청
test(
    "일반 사용자",
    Challenge(
        opponent="RandomPlayer",
        board_size=19,
        speed="blitz",
        rules="korean",
        handicap=0,
        ranked=True,
    ),
)


# 13x13
test(
    "13x13",
    Challenge(
        opponent="teacher_K.O bot",
        board_size=13,
        speed="blitz",
        rules="korean",
        handicap=0,
        ranked=True,
    ),
)


# 일본식 룰
test(
    "일본식 룰",
    Challenge(
        opponent="teacher_K.O bot",
        board_size=19,
        speed="blitz",
        rules="japanese",
        handicap=0,
        ranked=True,
    ),
)


# 학습 모드에서 핸디캡
test(
    "학습 모드 핸디캡",
    Challenge(
        opponent="teacher_K.O bot",
        board_size=19,
        speed="blitz",
        rules="korean",
        handicap=2,
        ranked=False,
    ),
)
