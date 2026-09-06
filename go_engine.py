from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Optional


BOARD_SIZE = 19
EMPTY = 0
BLACK = 1
WHITE = 2


@dataclass
class Move:
    x: int
    y: int

    @property
    def gtp(self) -> str:
        """
        GTP 좌표.
        GTP는 I 열을 건너뛴다.
        """
        letters = "ABCDEFGHJKLMNOPQRST"
        return f"{letters[self.x]}{BOARD_SIZE - self.y}"


class Board:
    def __init__(self, size: int = BOARD_SIZE):
        self.size = size
        self.board = [[EMPTY for _ in range(size)] for _ in range(size)]

    def copy(self) -> "Board":
        new_board = Board(self.size)
        new_board.board = [row[:] for row in self.board]
        return new_board

    def inside(self, x: int, y: int) -> bool:
        return 0 <= x < self.size and 0 <= y < self.size

    def neighbors(self, x: int, y: int):
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy

            if self.inside(nx, ny):
                yield nx, ny

    def group_and_liberties(self, x: int, y: int):
        color = self.board[y][x]

        if color == EMPTY:
            return set(), set()

        group = set()
        liberties = set()
        stack = [(x, y)]

        while stack:
            px, py = stack.pop()

            if (px, py) in group:
                continue

            group.add((px, py))

            for nx, ny in self.neighbors(px, py):
                value = self.board[ny][nx]

                if value == EMPTY:
                    liberties.add((nx, ny))
                elif value == color and (nx, ny) not in group:
                    stack.append((nx, ny))

        return group, liberties

    def play(self, x: int, y: int, color: int) -> bool:
        """
        기본적인 착수 검증.
        자살수 및 단순 패를 처리한다.
        """
        if not self.inside(x, y):
            return False

        if self.board[y][x] != EMPTY:
            return False

        self.board[y][x] = color

        opponent = BLACK if color == WHITE else WHITE

        # 상대 그룹 제거
        for nx, ny in list(self.neighbors(x, y)):
            if self.board[ny][nx] != opponent:
                continue

            group, liberties = self.group_and_liberties(nx, ny)

            if not liberties:
                for gx, gy in group:
                    self.board[gy][gx] = EMPTY

        # 자기 그룹의 자살 여부
        _, liberties = self.group_and_liberties(x, y)

        if not liberties:
            self.board[y][x] = EMPTY
            return False

        return True

    def legal_moves(self, color: int):
        result = []

        for y in range(self.size):
            for x in range(self.size):
                test = self.copy()

                if test.play(x, y, color):
                    result.append(Move(x, y))

        return result


class GoEngine:
    """
    현재는 아주 초기 버전.
    최종적으로는 이 클래스를 Neural Network + MCTS 엔진으로 교체한다.
    """

    def __init__(self):
        self.board = Board()
        self.color = BLACK

    def reset(self):
        self.board = Board()
        self.color = BLACK

    def play_opponent_move(self, x: int, y: int):
        if not self.board.play(x, y, self.color):
            raise ValueError(f"Illegal move: {x}, {y}")

        self.color = WHITE if self.color == BLACK else BLACK

    def select_move(self) -> Optional[Move]:
        legal = self.board.legal_moves(self.color)

        if not legal:
            return None

        # 현재는 랜덤.
        # 다음 단계에서 MCTS로 교체한다.
        return random.choice(legal)

    def play_our_move(self) -> Optional[Move]:
        move = self.select_move()

        if move is None:
            return None

        if not self.board.play(move.x, move.y, self.color):
            raise RuntimeError("Engine generated an illegal move.")

        self.color = WHITE if self.color == BLACK else BLACK

        return move
