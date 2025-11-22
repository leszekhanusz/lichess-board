import chess
from pytestqt.qtbot import QtBot

from lichess_board import ChessBoardWidget


def test_chess960_white_kingside_castling(qtbot: QtBot) -> None:
    """Test castling in Chess960 mode - white kingside."""
    widget = ChessBoardWidget()
    qtbot.addWidget(widget)
    widget.show()
    qtbot.waitExposed(widget)

    # Create a Chess960 board with a specific position
    # Position 518: RNBQKBNR (same as standard, but with chess960 flag)
    board = chess.Board(
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", chess960=True
    )

    # Set up position where white can castle
    board.push_san("e4")
    board.push_san("e5")
    board.push_san("Nf3")
    board.push_san("Nc6")
    board.push_san("Bc4")
    board.push_san("Bc5")

    widget.set_board(board)

    # Verify it's a Chess960 board
    assert widget._board.chess960 is True

    # Perform kingside castling
    castle_move = chess.Move.from_uci("e1g1")
    assert widget._board.is_castling(castle_move)

    # This should trigger the chess960 branch: if self._board.chess960:
    widget.play_move(castle_move, animate=True)

    # Wait for animation
    qtbot.wait(1000)

    # Verify castling happened
    assert widget._board.piece_at(chess.G1) == chess.Piece(chess.KING, chess.WHITE)
    assert widget._board.piece_at(chess.F1) == chess.Piece(chess.ROOK, chess.WHITE)
    assert widget._board.piece_at(chess.E1) is None
    assert widget._board.piece_at(chess.H1) is None


def test_chess960_white_queenside_castling(qtbot: QtBot) -> None:
    """Test castling in Chess960 mode - white queenside."""
    widget = ChessBoardWidget()
    qtbot.addWidget(widget)
    widget.show()
    qtbot.waitExposed(widget)

    # Create a Chess960 board
    board = chess.Board(
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", chess960=True
    )

    # Set up position where white can castle queenside
    board.push_san("d4")
    board.push_san("d5")
    board.push_san("Nc3")
    board.push_san("Nc6")
    board.push_san("Bf4")
    board.push_san("Bf5")
    board.push_san("Qd2")
    board.push_san("Qd7")

    widget.set_board(board)

    # Verify it's a Chess960 board
    assert widget._board.chess960 is True

    # Perform queenside castling
    castle_move = chess.Move.from_uci("e1c1")
    assert widget._board.is_castling(castle_move)

    # This should trigger the chess960 branch in _get_castling_info
    widget.play_move(castle_move, animate=True)

    # Wait for animation
    qtbot.wait(1000)

    # Verify castling happened
    assert widget._board.piece_at(chess.C1) == chess.Piece(chess.KING, chess.WHITE)
    assert widget._board.piece_at(chess.D1) == chess.Piece(chess.ROOK, chess.WHITE)


def test_chess960_black_kingside_castling(qtbot: QtBot) -> None:
    """Test castling in Chess960 mode - black kingside."""
    widget = ChessBoardWidget()
    qtbot.addWidget(widget)
    widget.show()
    qtbot.waitExposed(widget)

    # Create a Chess960 board
    board = chess.Board(
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", chess960=True
    )

    # Set up position where black can castle kingside
    board.push_san("e4")
    board.push_san("e5")
    board.push_san("Nc3")
    board.push_san("Nf6")
    board.push_san("Bc4")
    board.push_san("Bc5")
    board.push_san("d3")  # White's turn, arbitrary move

    widget.set_board(board)

    # Verify it's a Chess960 board
    assert widget._board.chess960 is True

    # Perform black kingside castling
    castle_move = chess.Move.from_uci("e8g8")
    assert widget._board.is_castling(castle_move)

    widget.play_move(castle_move, animate=True)

    # Wait for animation
    qtbot.wait(1000)

    # Verify castling happened
    assert widget._board.piece_at(chess.G8) == chess.Piece(chess.KING, chess.BLACK)
    assert widget._board.piece_at(chess.F8) == chess.Piece(chess.ROOK, chess.BLACK)


def test_chess960_black_queenside_castling(qtbot: QtBot) -> None:
    """Test castling in Chess960 mode - black queenside."""
    widget = ChessBoardWidget()
    qtbot.addWidget(widget)
    widget.show()
    qtbot.waitExposed(widget)

    # Create a Chess960 board
    board = chess.Board(
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", chess960=True
    )

    # Set up position where black can castle queenside
    board.push_san("e4")
    board.push_san("d5")
    board.push_san("Nc3")
    board.push_san("Nc6")
    board.push_san("Bc4")
    board.push_san("Bf5")
    board.push_san("d3")
    board.push_san("Qd7")
    board.push_san("Be3")  # White's turn

    widget.set_board(board)

    # Verify it's a Chess960 board
    assert widget._board.chess960 is True

    # Perform black queenside castling
    castle_move = chess.Move.from_uci("e8c8")
    assert widget._board.is_castling(castle_move)

    widget.play_move(castle_move, animate=True)

    # Wait for animation
    qtbot.wait(1000)

    # Verify castling happened
    assert widget._board.piece_at(chess.C8) == chess.Piece(chess.KING, chess.BLACK)
    assert widget._board.piece_at(chess.D8) == chess.Piece(chess.ROOK, chess.BLACK)


def test_chess960_undo_castling(qtbot: QtBot) -> None:
    """Test undoing castling in Chess960 mode."""
    widget = ChessBoardWidget()
    qtbot.addWidget(widget)
    widget.show()
    qtbot.waitExposed(widget)

    # Create a Chess960 board
    board = chess.Board(
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", chess960=True
    )

    # Set up position where white can castle
    board.push_san("e4")
    board.push_san("e5")
    board.push_san("Nf3")
    board.push_san("Nc6")
    board.push_san("Bc4")
    board.push_san("Bc5")

    widget.set_board(board)

    # Store FEN before castling
    fen_before = widget._board.fen()

    # Castle
    castle_move = chess.Move.from_uci("e1g1")
    widget.play_move(castle_move, animate=False)

    # Undo with animation - should also use chess960 logic
    widget.undo_move(animate=True)

    # Wait for animation
    qtbot.wait(1000)

    # Verify position restored
    assert widget._board.fen() == fen_before
    assert widget._board.piece_at(chess.E1) == chess.Piece(chess.KING, chess.WHITE)
    assert widget._board.piece_at(chess.H1) == chess.Piece(chess.ROOK, chess.WHITE)
