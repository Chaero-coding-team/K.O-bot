from __future__ import annotations

import sys
import random
import traceback

from go_engine import Board, BLACK, WHITE


BOARD_SIZE = 19


GTP_COLUMNS = "ABCDEFGHJKLMNOPQRST"


def gtp_to_xy(vertex: str):
    vertex = vertex.strip().upper()

    if vertex == "PASS":
        return None

    if len(vertex) < 2:
        raise ValueError("잘못된 좌표")

    column = vertex[0]

    if column not in GTP_COLUMNS:
        raise ValueError("잘못된 열")

    try:
        row = int(vertex[1:])
    except ValueError:
        raise ValueError("잘못된 행")

    x = GTP_COLUMNS.index(column)
    y = BOARD_SIZE - row

    if not (0 <= x < BOARD_SIZE):
        raise ValueError("X 범위 오류")

    if not (0 <= y < BOARD_SIZE):
        raise ValueError("Y 범위 오류")

    return x, y


def xy_to_gtp(x: int, y: int):
    return f"{GTP_COLUMNS[x]}{BOARD_SIZE - y}"


class GTPEngine:

    def __init__(self):
        self.board = Board(BOARD_SIZE)
        self.komi = 6.5
        self.color_to_move = BLACK

    def reset(self):
        self.board = Board(BOARD_SIZE)
        self.color_to_move = BLACK

    def play(self, color: int, vertex: str):
        if vertex.lower() == "pass":
            self.color_to_move = (
                WHITE if color == BLACK else BLACK
            )
            return True

        xy = gtp_to_xy(vertex)

        if xy is None:
            return True

        x, y = xy

        if not self.board.play(x, y, color):
            return False

        self.color_to_move = (
            WHITE if color == BLACK else BLACK
        )

        return True

    def genmove(self, color: int):
        legal_moves = self.board.legal_moves(color)

        if not legal_moves:
            return "pass"

        # 현재는 테스트용 랜덤 선택.
        # 나중에 이 부분을 MCTS + Neural Network로 교체한다.
        move = random.choice(legal_moves)

        success = self.board.play(
            move.x,
            move.y,
            color
        )

        if not success:
            return "pass"

        self.color_to_move = (
            WHITE if color == BLACK else BLACK
        )

        return xy_to_gtp(
            move.x,
            move.y
        )

    def handle(self, command: str):

        parts = command.strip().split()

        if not parts:
            return None

        cmd = parts[0].lower()

        try:

            if cmd == "protocol_version":
                return "2"

            if cmd == "name":
                return "K.O bot"

            if cmd == "version":
                return "0.1.0"

            if cmd == "list_commands":
                return (
                    "protocol_version\n"
                    "name\n"
                    "version\n"
                    "list_commands\n"
                    "boardsize\n"
                    "clear_board\n"
                    "komi\n"
                    "play\n"
                    "genmove\n"
                    "undo\n"
                    "quit"
                )

            if cmd == "boardsize":

                if len(parts) != 2:
                    return "? boardsize requires size"

                size = int(parts[1])

                if size != 19:
                    return "? only 19x19 is supported"

                self.reset()

                return ""

            if cmd == "clear_board":
                self.reset()
                return ""

            if cmd == "komi":

                if len(parts) != 2:
                    return "? komi requires value"

                self.komi = float(parts[1])

                return ""

            if cmd == "play":

                if len(parts) != 3:
                    return "? play COLOR VERTEX"

                color_text = parts[1].lower()

                if color_text == "black":
                    color = BLACK
                elif color_text == "white":
                    color = WHITE
                else:
                    return "? invalid color"

                if not self.play(color, parts[2]):
                    return "? illegal move"

                return ""

            if cmd == "genmove":

                if len(parts) != 2:
                    return "? genmove COLOR"

                color_text = parts[1].lower()

                if color_text == "black":
                    color = BLACK
                elif color_text == "white":
                    color = WHITE
                else:
                    return "? invalid color"

                move = self.genmove(color)

                return move

            if cmd == "undo":
                # 아직 undo history는 구현하지 않음
                return "? undo not implemented"

            if cmd == "quit":
                return "__QUIT__"

            return "? unknown command"

        except Exception as exc:

            print(
                f"GTP ERROR: {exc}",
                file=sys.stderr,
                flush=True
            )

            return f"? {exc}"

    def run(self):

        print(
            "= K.O bot ready",
            flush=True
        )

        for line in sys.stdin:

            line = line.strip()

            if not line:
                continue

            response = self.handle(line)

            if response == "__QUIT__":
                print(
                    "=",
                    flush=True
                )
                break

            if response is None:
                continue

            if response.startswith("?"):
                print(
                    response,
                    flush=True
                )
            else:
                print(
                    "=",
                    flush=True
                )

                if response:
                    print(
                        response,
                        flush=True
                    )

                print(
                    "",
                    flush=True
                )


if __name__ == "__main__":

    try:
        engine = GTPEngine()
        engine.run()

    except Exception:
        traceback.print_exc(
            file=sys.stderr
        )
        sys.exit(1)
