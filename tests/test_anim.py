import sys
import chess
from PySide6.QtWidgets import QApplication
from python_chess_board import ChessBoardWidget
from PySide6.QtCore import QTimer


def test_animation() -> None:
    app = QApplication(sys.argv)
    widget = ChessBoardWidget()
    widget.show()

    # Setup a move to animate
    move = chess.Move.from_uci("e2e4")
    print(f"Animating move: {move}")

    # Trigger animation
    try:
        widget.play_move(move, animate=True)
        print("Animation started successfully")
    except AttributeError as e:
        print(f"Caught expected error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Caught unexpected error: {e}")
        sys.exit(1)

    # Let it run for a bit
    QTimer.singleShot(1000, app.quit)
    app.exec()
    print("Test finished")


if __name__ == "__main__":
    test_animation()
