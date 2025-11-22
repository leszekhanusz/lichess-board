import os
from typing import TYPE_CHECKING

import chess
from PySide6.QtCore import QPointF, QSize, Qt
from PySide6.QtGui import QImage, QMouseEvent

from lichess_board import ChessBoardWidget

if TYPE_CHECKING:
    from pytestqt.qtbot import QtBot

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets", "images")
SIZE = QSize(400, 400)


def compare_images(widget: ChessBoardWidget, reference_filename: str) -> None:
    """Render widget and compare with reference image."""
    # Render widget
    image = QImage(widget.size(), QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    widget.render(image)

    # Load reference
    ref_path = os.path.join(ASSETS_DIR, reference_filename)
    assert os.path.exists(ref_path), f"Reference image not found: {ref_path}"

    ref_image = QImage(ref_path)
    assert not ref_image.isNull(), f"Failed to load reference image: {ref_path}"

    # Compare size
    assert (
        image.size() == ref_image.size()
    ), f"Size mismatch: {image.size()} != {ref_image.size()}"

    # Compare pixels
    # Note: This is a strict pixel-by-pixel comparison.
    # It might be fragile across different environments.
    # Ensuring that the QT_QPA_PLATFORM is set to offscreen seems to allow this
    # This is now done in conftest.py
    assert image == ref_image, f"Image content mismatch for {reference_filename}"


def test_initial_board(qtbot: "QtBot") -> None:
    widget = ChessBoardWidget()
    qtbot.addWidget(widget)
    widget.resize(SIZE)
    widget.show()
    qtbot.waitExposed(widget)

    compare_images(widget, "initial_board.png")


def test_initial_board_flipped(qtbot: "QtBot") -> None:
    widget = ChessBoardWidget()
    qtbot.addWidget(widget)
    widget.resize(SIZE)
    widget.set_flipped(True)
    widget.show()
    qtbot.waitExposed(widget)

    compare_images(widget, "initial_board_flipped.png")


def test_italian_opening_board(qtbot: "QtBot") -> None:
    italian_fen = "r1bqk1nr/pppp1ppp/2n5/2b1p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4"
    board = chess.Board(italian_fen)
    widget = ChessBoardWidget(board=board)
    qtbot.addWidget(widget)
    widget.resize(SIZE)
    widget.show()
    qtbot.waitExposed(widget)

    compare_images(widget, "italian_opening_board.png")


def test_italian_opening_moves(qtbot: "QtBot") -> None:
    widget = ChessBoardWidget()
    qtbot.addWidget(widget)
    widget.resize(SIZE)
    widget.show()
    qtbot.waitExposed(widget)

    moves = ["e2e4", "e7e5", "g1f3", "b8c6", "f1c4", "f8c5"]
    for uci in moves:
        widget.play_move(chess.Move.from_uci(uci), animate=False)

    compare_images(widget, "italian_opening_moves.png")


def test_white_pawn_selected(qtbot: "QtBot") -> None:
    widget = ChessBoardWidget()
    qtbot.addWidget(widget)
    widget.resize(SIZE)
    widget.show()
    qtbot.waitExposed(widget)

    # Select e2 pawn
    # e2: file e (4), rank 2.
    # visual_row = 7 - 1 = 6.
    # visual_col = 4.
    # x = 4 * 50 + 25 = 225.
    # y = 6 * 50 + 25 = 325.
    click_point = QPointF(225, 325)

    # Use direct event to match generator behavior exactly

    event = QMouseEvent(
        QMouseEvent.Type.MouseButtonPress,
        click_point,
        click_point,
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )
    widget.mousePressEvent(event)

    compare_images(widget, "white_pawn_selected.png")


def test_scandinavian_capture(qtbot: "QtBot") -> None:
    widget = ChessBoardWidget()
    qtbot.addWidget(widget)
    widget.resize(SIZE)
    widget.show()
    qtbot.waitExposed(widget)

    widget.play_move(chess.Move.from_uci("e2e4"), animate=False)
    widget.play_move(chess.Move.from_uci("d7d5"), animate=False)

    # Select e4 pawn
    # e4: file e (4), rank 3.
    # visual_row = 7 - 3 = 4.
    # visual_col = 4.
    # x = 4 * 50 + 25 = 225.
    # y = 4 * 50 + 25 = 225.
    click_point = QPointF(225, 225)

    event = QMouseEvent(
        QMouseEvent.Type.MouseButtonPress,
        click_point,
        click_point,
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )
    widget.mousePressEvent(event)

    compare_images(widget, "scandinavian_capture.png")
