import sys

import chess
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from python_chess_board import ChessBoardWidget


def test_check_indicator() -> None:
    app = QApplication(sys.argv)
    widget = ChessBoardWidget()
    widget.show()
    widget.resize(600, 600)

    # Set up a position where white is in check
    # Scholar's mate position
    board = chess.Board()
    board.push_san("e4")
    board.push_san("e5")
    board.push_san("Bc4")
    board.push_san("Nc6")
    board.push_san("Qh5")
    board.push_san("Nf6")
    board.push_san("Qxf7+")  # Check!

    widget.set_board(board)

    print("Board is in check:", board.is_check())
    king_square = board.king(board.turn)
    if king_square is not None:
        print("King square:", chess.square_name(king_square))

    # Close after 3 seconds
    QTimer.singleShot(3000, app.quit)

    app.exec()
    print("Test finished")


if __name__ == "__main__":
    test_check_indicator()
