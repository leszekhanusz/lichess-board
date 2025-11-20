import random
import sys

import chess
from PySide6.QtCore import QTimer
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
        self.player_color = chess.WHITE  # Player plays white by default

    def toggle_flip(self) -> None:
        self.flipped = not self.flipped
        self.board_widget.set_flipped(self.flipped)
        # When flipping, switch player color
        self.player_color = chess.BLACK if self.flipped else chess.WHITE

        # If it's now the opponent's turn after flipping, make an automatic move
        board = self.board_widget._board
        if not board.is_game_over() and board.turn != self.player_color:
            QTimer.singleShot(500, self.make_opponent_move)

    def on_move_played(self, move: chess.Move) -> None:
        print(f"Move played: {move}")

        # Check if it's the player's move (not the automatic opponent move)
        board = self.board_widget._board

        # If the game is over, don't make automatic move
        if board.is_game_over():
            print("Game over!")
            return

        # If it's now the opponent's turn, make an automatic move after a delay
        if board.turn != self.player_color:
            QTimer.singleShot(500, self.make_opponent_move)

    def make_opponent_move(self) -> None:
        board = self.board_widget._board

        # Get all legal moves
        legal_moves = list(board.legal_moves)

        if legal_moves:
            # Choose a random move
            random_move = random.choice(legal_moves)
            print(f"Opponent plays: {random_move}")

            # Play the move with animation
            self.board_widget.play_move(random_move, animate=True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
