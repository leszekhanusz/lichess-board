import sys

import chess
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from python_chess_board import ChessBoardWidget


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Python Chess Board Example")
        self.resize(600, 650)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.board_widget = ChessBoardWidget()
        layout.addWidget(self.board_widget)

        self.flip_btn = QPushButton("Flip Board")
        self.flip_btn.clicked.connect(self.toggle_flip)
        layout.addWidget(self.flip_btn)

        self.board_widget.move_played.connect(self.on_move_played)

        self.flipped = False

    def toggle_flip(self) -> None:
        self.flipped = not self.flipped
        self.board_widget.set_flipped(self.flipped)

    def on_move_played(self, move: chess.Move) -> None:
        print(f"Move played: {move}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
