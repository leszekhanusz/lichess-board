from typing import List, Optional, Tuple

import chess
from PySide6.QtCore import QPointF, QRectF, Qt, QTimer, Signal
from PySide6.QtGui import QMouseEvent, QPainter, QPaintEvent, QResizeEvent
from PySide6.QtWidgets import QWidget

from .renderer import Renderer


class ChessBoardWidget(QWidget):
    """
    A PySide6 widget that displays a chess board and allows interaction.
    """

    move_played = Signal(chess.Move)

    def __init__(
        self, parent: Optional[QWidget] = None, board: Optional[chess.Board] = None
    ):
        super().__init__(parent)

        self._board = board if board else chess.Board()
        self._renderer = Renderer()
        self._flipped = False

        # Interaction state
        self._selected_square: Optional[int] = None
        self._dragged_square: Optional[int] = None
        self._drag_pos: QPointF = QPointF()
        self._is_dragging = False
        self._legal_moves: List[chess.Move] = []
        self._hover_square: Optional[int] = None

        # Animation state - supports multiple pieces (e.g., castling)
        # List of (piece, start_pos, end_pos) tuples
        self._animating_pieces: List[Tuple[chess.Piece, QPointF, QPointF]] = []
        self._anim_timer = QTimer()
        self._anim_timer.setInterval(16)  # ~60 FPS
        self._anim_timer.timeout.connect(self._update_animation)
        self._anim_progress = 0.0
        self._anim_move: Optional[chess.Move] = None

        self.setMouseTracking(True)  # Enable mouse tracking for hover effects
        self.setMinimumSize(200, 200)

    def set_board(self, board: chess.Board) -> None:
        self._board = board
        self._selected_square = None
        self._dragged_square = None
        self._legal_moves = []
        self.update()

    def set_flipped(self, flipped: bool) -> None:
        self._flipped = flipped
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self._get_board_rect()

        # Draw board and coordinates
        self._renderer.draw_board(painter, rect, self._flipped)

        # Highlight last move
        if self._board.move_stack:
            self._renderer.highlight_last_move(
                painter, rect, self._board.peek(), self._flipped
            )

        # Highlight selected square
        if self._selected_square is not None:
            self._renderer.highlight_square(
                painter,
                rect,
                self._selected_square,
                self._renderer.selected_color,
                self._flipped,
            )

        # Highlight hover square (if it's a legal move target)
        if self._hover_square is not None:
            # Check if hover square is a valid target for the selected piece
            if self._selected_square is not None:
                move = self._find_move(self._selected_square, self._hover_square)
                if move:
                    self._renderer.highlight_square(
                        painter,
                        rect,
                        self._hover_square,
                        self._renderer.selected_color,
                        self._flipped,
                    )

        # Draw check indicator if king is in check
        if self._board.is_check():
            # Find the king square for the side in check
            king_square = self._board.king(self._board.turn)
            if king_square is not None:
                self._renderer.draw_check_indicator(
                    painter, rect, king_square, self._flipped
                )

        # Draw pieces
        # Build list of squares to exclude (animating pieces)
        exclude_squares = []
        if self._animating_pieces and self._anim_move:
            # For castling, exclude both king and rook source squares
            if self._board.is_castling(self._anim_move):
                exclude_squares.append(self._anim_move.from_square)
                # Determine rook source square
                king_to = self._anim_move.to_square
                if king_to == chess.G1:
                    exclude_squares.append(chess.H1)
                elif king_to == chess.C1:
                    exclude_squares.append(chess.A1)
                elif king_to == chess.G8:
                    exclude_squares.append(chess.H8)
                elif king_to == chess.C8:
                    exclude_squares.append(chess.A8)
            else:
                exclude_squares.append(self._anim_move.from_square)

        # Draw all pieces, excluding animating ones
        square_size = rect.width() / 8
        for square in chess.SQUARES:
            if square in exclude_squares:
                continue
            if square == self._dragged_square and self._is_dragging:
                # Draw dragged piece faded
                piece = self._board.piece_at(square)
                if piece:
                    rank = chess.square_rank(square)
                    file = chess.square_file(square)
                    if self._flipped:
                        visual_row = rank
                        visual_col = 7 - file
                    else:
                        visual_row = 7 - rank
                        visual_col = file
                    x = rect.x() + visual_col * square_size
                    y = rect.y() + visual_row * square_size
                    color_prefix = "w" if piece.color == chess.WHITE else "b"
                    piece_code = f"{color_prefix}{piece.symbol().upper()}"
                    renderer = self._renderer.piece_renderers.get(piece_code)
                    if renderer:
                        painter.save()
                        painter.setOpacity(0.5)
                        renderer.render(painter, QRectF(x, y, square_size, square_size))
                        painter.restore()
            else:
                piece = self._board.piece_at(square)
                if piece:
                    rank = chess.square_rank(square)
                    file = chess.square_file(square)
                    if self._flipped:
                        visual_row = rank
                        visual_col = 7 - file
                    else:
                        visual_row = 7 - rank
                        visual_col = file
                    x = rect.x() + visual_col * square_size
                    y = rect.y() + visual_row * square_size
                    color_prefix = "w" if piece.color == chess.WHITE else "b"
                    piece_code = f"{color_prefix}{piece.symbol().upper()}"
                    renderer = self._renderer.piece_renderers.get(piece_code)
                    if renderer:
                        renderer.render(painter, QRectF(x, y, square_size, square_size))

        # Draw legal moves hints
        if self._selected_square is not None:
            self._renderer.draw_legal_moves(
                painter,
                rect,
                self._legal_moves,
                self._flipped,
                self._board,
                hide_square=self._hover_square,
            )

        # Draw dragged piece
        if self._is_dragging and self._dragged_square is not None:
            piece = self._board.piece_at(self._dragged_square)
            if piece:
                square_size = rect.width() / 8
                self._renderer.draw_dragged_piece(
                    painter,
                    piece,
                    (self._drag_pos.x(), self._drag_pos.y()),
                    square_size,
                )

        # Draw animating pieces
        if self._animating_pieces:
            square_size = rect.width() / 8
            for piece, start_pos, end_pos in self._animating_pieces:
                # Linear interpolation
                current_x = (
                    start_pos.x() + (end_pos.x() - start_pos.x()) * self._anim_progress
                )
                current_y = (
                    start_pos.y() + (end_pos.y() - start_pos.y()) * self._anim_progress
                )
                self._renderer.draw_dragged_piece(
                    painter,
                    piece,
                    (current_x, current_y),
                    square_size,
                )

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() != Qt.MouseButton.LeftButton:
            return

        square = self._pos_to_square(event.position())
        if square is None:
            self._clear_selection()
            return

        piece = self._board.piece_at(square)

        # If clicking on a square that is a legal move for currently selected piece
        if self._selected_square is not None:
            move = self._find_move(self._selected_square, square)
            if move:
                self._make_move(move)
                self._clear_selection()
                return

        # Select new piece
        if piece and piece.color == self._board.turn:
            self._selected_square = square
            self._dragged_square = square
            self._is_dragging = True
            self._drag_pos = event.position()
            self._legal_moves = [
                m for m in self._board.legal_moves if m.from_square == square
            ]
            self.update()
        else:
            self._clear_selection()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        square = self._pos_to_square(event.position())
        self._hover_square = square

        if self._is_dragging:
            self._drag_pos = event.position()
            self.update()
        else:
            # Just update for hover effects if needed
            # Only update if hover state changed significantly
            # or if we want to show hover highlight for moves
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if not self._is_dragging:
            return

        square = self._pos_to_square(event.position())

        if square is not None and self._dragged_square is not None:
            move = self._find_move(self._dragged_square, square)
            if move:
                self._make_move(move)
                self._clear_selection()
            else:
                # If released on same square, keep selected (click behavior)
                if square == self._dragged_square:
                    self._is_dragging = False
                    self.update()
                else:
                    # Invalid drop, reset
                    # If we want to keep selection when dropping on invalid square
                    # But usually dropping on invalid square deselects
                    # Lichess: snaps back, keeps selection?
                    # Let's keep selection but stop dragging.
                    self._is_dragging = False
                    self.update()
        else:
            self._is_dragging = False
            self.update()

    def resizeEvent(self, event: QResizeEvent) -> None:
        # Maintain aspect ratio? Or just fill?
        # Board is usually square.
        # Let's assume the widget can be any shape but we draw square board centered
        # For now, renderer assumes square rect.
        # We should probably force aspect ratio or handle non-square rects in renderer.
        # Renderer uses rect.width() / 8 for square size.
        # Let's enforce square aspect ratio in resize or just use the smaller dimension.
        super().resizeEvent(event)

        # We can make the content rect square

        # But for now let's just update.
        self.update()

    def _pos_to_square(self, pos: QPointF) -> Optional[int]:
        rect = self._get_board_rect()

        if not rect.contains(pos):
            return None

        square_size = rect.width() / 8

        # Relative position
        rel_x = pos.x() - rect.x()
        rel_y = pos.y() - rect.y()

        col = int(rel_x / square_size)
        row = int(rel_y / square_size)

        if col < 0 or col > 7 or row < 0 or row > 7:
            return None

        if self._flipped:
            rank = row + 1  # row 0 -> rank 1
            file = 7 - col  # col 0 -> file h
        else:
            rank = 8 - row  # row 0 -> rank 8
            file = col  # col 0 -> file a

        return int(chess.square(file, rank - 1))

    def _find_move(self, from_sq: int, to_sq: int) -> Optional[chess.Move]:
        # Handle promotion: auto-promote to Queen for now or check all variants
        # python-chess moves include promotion.
        # If we need promotion, we should check if a move is a promotion move.

        for move in self._board.legal_moves:
            if move.from_square == from_sq and move.to_square == to_sq:
                return move
        return None

    def _make_move(self, move: chess.Move) -> None:
        self.play_move(move, animate=False)

    def play_move(self, move: chess.Move, animate: bool = True) -> None:
        if animate:
            self._anim_move = move
            self._animating_pieces = []

            # Add king/main piece animation
            piece = self._board.piece_at(move.from_square)
            if piece:
                start_pos = self._get_square_center(move.from_square)
                end_pos = self._get_square_center(move.to_square)
                self._animating_pieces.append((piece, start_pos, end_pos))

            # Check if this is a castling move and add rook animation
            if self._board.is_castling(move):
                # Determine rook movement based on king's destination
                king_to = move.to_square

                if king_to == chess.G1:  # White kingside
                    rook_from, rook_to = chess.H1, chess.F1
                elif king_to == chess.C1:  # White queenside
                    rook_from, rook_to = chess.A1, chess.D1
                elif king_to == chess.G8:  # Black kingside
                    rook_from, rook_to = chess.H8, chess.F8
                elif king_to == chess.C8:  # Black queenside
                    rook_from, rook_to = chess.A8, chess.D8
                else:
                    rook_from, rook_to = None, None

                if rook_from is not None:
                    rook = self._board.piece_at(rook_from)
                    if rook:
                        rook_start = self._get_square_center(rook_from)
                        rook_end = self._get_square_center(rook_to)
                        self._animating_pieces.append((rook, rook_start, rook_end))

            self._anim_progress = 0.0
            self._anim_timer.start()
        else:
            self._board.push(move)
            self.move_played.emit(move)
            self.update()

    def _update_animation(self) -> None:
        self._anim_progress += 0.05  # Adjust speed
        if self._anim_progress >= 1.0:
            self._anim_progress = 1.0
            self._anim_timer.stop()
            if self._anim_move:
                self._board.push(self._anim_move)
                self.move_played.emit(self._anim_move)
            self._animating_pieces = []
            self._anim_move = None
            self.update()
            return

        # Animation continues, widget will interpolate in paintEvent
        self.update()

    def _get_square_center(self, square: int) -> QPointF:
        rect = self._get_board_rect()
        square_size = rect.width() / 8

        rank = chess.square_rank(square)
        file = chess.square_file(square)

        if self._flipped:
            visual_row = rank
            visual_col = 7 - file
        else:
            visual_row = 7 - rank
            visual_col = file

        x = rect.x() + visual_col * square_size + square_size / 2
        y = rect.y() + visual_row * square_size + square_size / 2
        return QPointF(x, y)

    def _get_board_rect(self) -> QRectF:
        w = self.width()
        h = self.height()
        s = min(w, h)

        x = (w - s) / 2
        y = (h - s) / 2

        return QRectF(x, y, s, s)

    def _clear_selection(self) -> None:
        self._selected_square = None
        self._dragged_square = None
        self._is_dragging = False
        self._legal_moves = []
        self.update()
