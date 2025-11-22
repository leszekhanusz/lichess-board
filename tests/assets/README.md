# Visual Regression Test Assets

This directory contains reference images used for visual regression testing.

## Regenerating Reference Images

If you need to regenerate the reference images (e.g., after intentional UI changes), run:

```bash
python tests/generate_test_images.py
```

**IMPORTANT:** The script automatically uses `QT_QPA_PLATFORM=offscreen` to ensure the generated images match the rendering environment used in GitHub Actions CI.

## Comparison Method

The tests use a fuzzy comparison (Root Mean Square difference) with a tolerance of 5.0 to allow for small rendering differences (antialiasing, font hinting) between environments. This makes the tests more robust than strict pixel-perfect equality.

## Image Files

- `initial_board.png` - Default chess board starting position
- `initial_board_flipped.png` - Starting position from black's perspective
- `italian_opening_board.png` - Italian opening position (from FEN)
- `italian_opening_moves.png` - Italian opening (played from moves)
- `white_pawn_selected.png` - Board with e2 pawn selected showing legal moves
- `scandinavian_capture.png` - Scandinavian defense with e4 pawn selected

## Troubleshooting

If visual regression tests fail in CI:
1. Ensure reference images were generated using offscreen rendering
2. Check that Qt/PySide6 versions match between local and CI
3. Verify no unintended UI changes were introduced
