from importlib.resources import files
from typing import Dict, Optional, Tuple

import chess
from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QPainter, QPen
from PySide6.QtSvg import QSvgRenderer


class Renderer:
    def __init__(self) -> None:
        self.light_color = QColor("#f0d9b5")
        self.dark_color = QColor("#b58863")
        self.highlight_color = QColor(155, 199, 0, 105)  # Lime with alpha
        self.selected_color = QColor(20, 85, 30, 128)  # Green with alpha
        self.move_hint_color = QColor(20, 85, 30, 50)  # Faint green

        self.piece_renderers: Dict[str, QSvgRenderer] = {}
        self.load_assets()

    def load_assets(self) -> None:
        pieces = [
            "wP",
            "wN",
            "wB",
            "wR",
            "wQ",
            "wK",
            "bP",
            "bN",
            "bB",
            "bR",
            "bQ",
            "bK",
        ]

        # Use importlib.resources to access package assets
        assets_path = files("python_chess_board").joinpath("assets")

        for p in pieces:
            svg_file = assets_path.joinpath(f"{p}.svg")
            # Read the SVG content and pass it to QSvgRenderer
            svg_data = svg_file.read_bytes()
            renderer = QSvgRenderer(svg_data)
            self.piece_renderers[p] = renderer

    def draw_board(self, painter: QPainter, rect: QRectF, flipped: bool) -> None:
        square_size = rect.width() / 8

        for row in range(8):
            for col in range(8):
                # Determine color
                is_light = (row + col) % 2 == 0
                color = self.light_color if is_light else self.dark_color

                x = rect.x() + col * square_size
                y = rect.y() + row * square_size

                painter.fillRect(QRectF(x, y, square_size, square_size), color)

                # Draw coordinates
                rank_text = ""
                file_text = ""

                actual_rank = 8 - row if not flipped else row + 1
                actual_file = (
                    chr(ord("a") + col) if not flipped else chr(ord("h") - col)
                )

                # Draw rank on the right-most column
                if col == 7:
                    rank_text = str(actual_rank)
                    # Draw at top-right of the square
                    text_color = self.dark_color if is_light else self.light_color
                    painter.setPen(text_color)
                    font = painter.font()
                    font.setPixelSize(int(square_size * 0.2))
                    painter.setFont(font)
                    painter.drawText(
                        QRectF(x, y + 2, square_size - 2, square_size),
                        Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight,
                        rank_text,
                    )

                # Draw file on the bottom-most row
                if row == 7:
                    file_text = actual_file
                    # Draw at bottom-left of the square
                    text_color = self.dark_color if is_light else self.light_color
                    painter.setPen(text_color)
                    font = painter.font()
                    font.setPixelSize(int(square_size * 0.2))
                    painter.setFont(font)
                    painter.drawText(
                        QRectF(x + 2, y, square_size, square_size - 2),
                        Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft,
                        file_text,
                    )

    def draw_pieces(
        self,
        painter: QPainter,
        rect: QRectF,
        board: chess.Board,
        flipped: bool,
        exclude_square: Optional[int] = None,
        faded_square: Optional[int] = None,
    ) -> None:
        square_size = rect.width() / 8

        for square in chess.SQUARES:
            if square == exclude_square:
                continue

            piece = board.piece_at(square)
            if piece:
                # Calculate position
                rank = chess.square_rank(square)
                file = chess.square_file(square)

                if flipped:
                    visual_row = rank
                    visual_col = 7 - file
                else:
                    visual_row = 7 - rank
                    visual_col = file

                x = rect.x() + visual_col * square_size
                y = rect.y() + visual_row * square_size

                piece_code = (
                    f"{'w' if piece.color == chess.WHITE else 'b'}"
                    f"{piece.symbol().upper()}"
                )
                renderer = self.piece_renderers.get(piece_code)
                if renderer:
                    if square == faded_square:
                        painter.save()
                        painter.setOpacity(0.5)
                        renderer.render(painter, QRectF(x, y, square_size, square_size))
                        painter.restore()
                    else:
                        renderer.render(painter, QRectF(x, y, square_size, square_size))

    def draw_dragged_piece(
        self,
        painter: QPainter,
        piece: chess.Piece,
        center_pos: Tuple[float, float],
        size: float,
    ) -> None:
        piece_code = (
            f"{'w' if piece.color == chess.WHITE else 'b'}{piece.symbol().upper()}"
        )
        renderer = self.piece_renderers.get(piece_code)
        if renderer:
            # Center the piece on the mouse cursor
            x = center_pos[0] - size / 2
            y = center_pos[1] - size / 2
            renderer.render(painter, QRectF(x, y, size, size))

    def draw_legal_moves(
        self,
        painter: QPainter,
        rect: QRectF,
        moves: list[chess.Move],
        flipped: bool,
        board: chess.Board,
        hide_square: Optional[int] = None,
    ) -> None:
        square_size = rect.width() / 8
        painter.setPen(Qt.PenStyle.NoPen)

        for move in moves:
            target = move.to_square
            if target == hide_square:
                continue

            rank = chess.square_rank(target)
            file = chess.square_file(target)

            if flipped:
                visual_row = rank
                visual_col = 7 - file
            else:
                visual_row = 7 - rank
                visual_col = file

            x = rect.x() + visual_col * square_size
            y = rect.y() + visual_row * square_size
            center_x = x + square_size / 2
            center_y = y + square_size / 2

            # Check if target is occupied (capture)
            if board.piece_at(target):
                color = self.move_hint_color
                # Draw ring for capture
                painter.setBrush(Qt.BrushStyle.NoBrush)
                pen = QPen(color)
                pen.setWidth(int(square_size * 0.1))
                painter.setPen(pen)
                painter.drawEllipse(
                    QRectF(
                        x + square_size * 0.1,
                        y + square_size * 0.1,
                        square_size * 0.8,
                        square_size * 0.8,
                    )
                )
                painter.setPen(Qt.PenStyle.NoPen)
            else:
                color = self.move_hint_color
                painter.setBrush(QBrush(color))
                radius = square_size * 0.15
                painter.drawEllipse(
                    QRectF(center_x - radius, center_y - radius, radius * 2, radius * 2)
                )

    def highlight_last_move(
        self, painter: QPainter, rect: QRectF, move: chess.Move, flipped: bool
    ) -> None:
        if not move:
            return

        self.highlight_square(
            painter, rect, move.from_square, self.highlight_color, flipped
        )
        self.highlight_square(
            painter, rect, move.to_square, self.highlight_color, flipped
        )

    def highlight_square(
        self, painter: QPainter, rect: QRectF, square: int, color: QColor, flipped: bool
    ) -> None:
        square_size = rect.width() / 8
        rank = chess.square_rank(square)
        file = chess.square_file(square)

        if flipped:
            visual_row = rank
            visual_col = 7 - file
        else:
            visual_row = 7 - rank
            visual_col = file

        x = rect.x() + visual_col * square_size
        y = rect.y() + visual_row * square_size

        painter.fillRect(QRectF(x, y, square_size, square_size), color)
