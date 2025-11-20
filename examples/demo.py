import random
import sys
from typing import List

import chess
from PySide6.QtCore import QByteArray, QSize, Qt, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from lichess_board import ChessBoardWidget

# SVG Icons matching the style
ICON_FIRST = """
<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M18.5 19V5M5.5 12L14.5 19V5L5.5 12Z" fill="#666666"/>
</svg>
"""

ICON_PREV = """
<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M15 19V5L6 12L15 19Z" fill="#666666"/>
</svg>
"""

ICON_NEXT = """
<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M9 5V19L18 12L9 5Z" fill="#666666"/>
</svg>
"""

ICON_LAST = """
<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M5.5 5V19M18.5 12L9.5 5V19L18.5 12Z" fill="#666666"/>
</svg>
"""


def create_icon(svg_content: str) -> QIcon:
    renderer = QSvgRenderer(QByteArray(svg_content.encode()))
    pixmap = QIcon.fromTheme("document-new").pixmap(24, 24)  # Dummy pixmap
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = pixmap.createMaskFromColor(
        Qt.GlobalColor.transparent, Qt.MaskMode.MaskOutColor
    )  # Just to get a painter

    # Actually we need to render to a pixmap
    from PySide6.QtGui import QPainter, QPixmap

    pixmap = QPixmap(24, 24)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Python Chess Board Example")
        self.resize(600, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(0)
        layout.setContentsMargins(20, 20, 20, 20)

        # Board
        self.board_widget = ChessBoardWidget()
        layout.addWidget(self.board_widget)

        # Navigation Bar
        nav_widget = QWidget()
        nav_widget.setFixedHeight(50)  # Restricted height
        nav_layout = QHBoxLayout(nav_widget)
        nav_layout.setContentsMargins(0, 10, 0, 0)
        nav_layout.setSpacing(5)  # Small spacing between buttons

        # Stylesheet for buttons
        # hsl(209, 66%, 84%) -> #bbdcf9 (approx) but Qt supports hsl/hsla
        button_style = """
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: hsl(209, 66%, 84%);
            }
            QPushButton:pressed {
                background-color: hsl(209, 66%, 70%);
            }
            QPushButton:disabled {
                opacity: 0.5;
            }
        """

        self.btn_first = QPushButton()
        self.btn_first.setIcon(create_icon(ICON_FIRST))
        self.btn_first.setIconSize(QSize(24, 24))
        self.btn_first.setStyleSheet(button_style)
        self.btn_first.clicked.connect(self.go_first)
        self.btn_first.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        self.btn_prev = QPushButton()
        self.btn_prev.setIcon(create_icon(ICON_PREV))
        self.btn_prev.setIconSize(QSize(24, 24))
        self.btn_prev.setStyleSheet(button_style)
        self.btn_prev.clicked.connect(self.go_prev)
        self.btn_prev.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        self.btn_next = QPushButton()
        self.btn_next.setIcon(create_icon(ICON_NEXT))
        self.btn_next.setIconSize(QSize(24, 24))
        self.btn_next.setStyleSheet(button_style)
        self.btn_next.clicked.connect(self.go_next)
        self.btn_next.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        self.btn_last = QPushButton()
        self.btn_last.setIcon(create_icon(ICON_LAST))
        self.btn_last.setIconSize(QSize(24, 24))
        self.btn_last.setStyleSheet(button_style)
        self.btn_last.clicked.connect(self.go_last)
        self.btn_last.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        # Add buttons to layout with equal stretch
        nav_layout.addWidget(self.btn_first, 1)
        nav_layout.addWidget(self.btn_prev, 1)
        nav_layout.addWidget(self.btn_next, 1)
        nav_layout.addWidget(self.btn_last, 1)

        layout.addWidget(nav_widget)

        # Flip button below
        self.flip_btn = QPushButton("Flip Board")
        self.flip_btn.clicked.connect(self.toggle_flip)
        layout.addWidget(self.flip_btn)

        self.board_widget.move_played.connect(self.on_move_played)

        self.flipped = False
        self.player_color = chess.WHITE

        # Game history
        self.move_history: List[chess.Move] = []
        self.current_move_index = -1  # -1 means start of game (no moves made)

        self.update_buttons()

    def toggle_flip(self) -> None:
        self.flipped = not self.flipped
        self.board_widget.set_flipped(self.flipped)
        self.player_color = chess.BLACK if self.flipped else chess.WHITE

        # Only trigger opponent move if we are at the latest position
        if self.is_at_latest():
            self.check_opponent_move()

    def on_move_played(self, move: chess.Move) -> None:
        print(f"Move played: {move}")

        # If we made a move from a previous position, we truncate the history
        if self.current_move_index < len(self.move_history) - 1:
            self.move_history = self.move_history[: self.current_move_index + 1]

        self.move_history.append(move)
        self.current_move_index += 1
        self.update_buttons()

        self.check_opponent_move()

    def check_opponent_move(self) -> None:
        board = self.board_widget._board
        if board.is_game_over():
            print("Game over!")
            return

        if board.turn != self.player_color:
            QTimer.singleShot(500, self.make_opponent_move)

    def make_opponent_move(self) -> None:
        # Ensure we are still at the latest position before making a move
        if not self.is_at_latest():
            return

        board = self.board_widget._board
        if board.turn == self.player_color:
            return

        legal_moves = list(board.legal_moves)
        if legal_moves:
            random_move = random.choice(legal_moves)
            print(f"Opponent plays: {random_move}")
            self.board_widget.play_move(random_move, animate=True)

    def is_at_latest(self) -> bool:
        return self.current_move_index == len(self.move_history) - 1

    def update_buttons(self) -> None:
        has_prev = self.current_move_index >= 0
        has_next = self.current_move_index < len(self.move_history) - 1

        self.btn_first.setEnabled(has_prev)
        self.btn_prev.setEnabled(has_prev)
        self.btn_next.setEnabled(has_next)
        self.btn_last.setEnabled(has_next)

    def go_first(self) -> None:
        while self.current_move_index >= 0:
            self.board_widget._board.pop()
            self.current_move_index -= 1
        self.board_widget.update()
        self.update_buttons()

    def go_prev(self) -> None:
        if self.current_move_index >= 0:
            self.board_widget._board.pop()
            self.current_move_index -= 1
            self.board_widget.update()
            self.update_buttons()

    def go_next(self) -> None:
        if self.current_move_index < len(self.move_history) - 1:
            move = self.move_history[self.current_move_index + 1]
            self.board_widget._board.push(move)
            self.current_move_index += 1
            self.board_widget.update()
            self.update_buttons()

    def go_last(self) -> None:
        while self.current_move_index < len(self.move_history) - 1:
            move = self.move_history[self.current_move_index + 1]
            self.board_widget._board.push(move)
            self.current_move_index += 1
        self.board_widget.update()
        self.update_buttons()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
