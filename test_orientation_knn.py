"""Focused validation for task 8.2 using tablero2 ground truth from entrenar_dual."""

import numpy as np
from PIL import Image

import app
from entrenar_dual import etiquetas


def expected_tablero2():
    labels, style, expected_angle = etiquetas("tablero2.png")
    expected = np.array([labels.get(index, "empty") for index in range(64)])
    return expected, style, expected_angle


def accuracy(classifications, expected):
    return int((np.asarray(classifications) == expected).sum())


def test_orientation_score_priorities():
    acceptable = ["empty"] * 64
    unacceptable = ["empty"] * 64
    unacceptable[0] = "wP"
    assert app.orientation_score(acceptable, 180) > app.orientation_score(
        unacceptable, 0
    )

    one_extreme_pawn = unacceptable
    two_extreme_pawns = unacceptable.copy()
    two_extreme_pawns[63] = "bP"
    assert app.orientation_score(one_extreme_pawn, 180) > app.orientation_score(
        two_extreme_pawns, 0
    )

    one_piece = acceptable.copy()
    one_piece[27] = "wN"
    two_pieces = one_piece.copy()
    two_pieces[36] = "bN"
    assert app.orientation_score(two_pieces, 180) > app.orientation_score(
        one_piece, 0
    )
    assert app.orientation_score(one_piece, 0) > app.orientation_score(one_piece, 180)


def main():
    test_orientation_score_priorities()
    expected, expected_style, expected_angle = expected_tablero2()
    image = Image.open("ejemplos/tablero2.png")

    before = app.analyze_board_orientation(image, margen=0, automatic=False)
    automatic = app.analyze_board_orientation(image, margen=0, automatic=True)
    manual = app.analyze_board_orientation(
        image.rotate(180), margen=0, automatic=False
    )

    before_accuracy = accuracy(before["classifications"], expected)
    automatic_accuracy = accuracy(automatic["classifications"], expected)
    manual_accuracy = accuracy(manual["classifications"], expected)

    print(f"expected_style={expected_style}, expected_orientation={expected_angle}")
    print(
        f"before: orientation=0, accuracy={before_accuracy}/64, "
        f"score={before['score']}"
    )
    print(
        f"automatic: orientation={automatic['rotation']}, "
        f"accuracy={automatic_accuracy}/64, score={automatic['score']}"
    )
    print(f"manual: orientation=180, accuracy={manual_accuracy}/64")

    assert expected_angle == 180
    assert automatic["rotation"] == 0
    assert before_accuracy == automatic_accuracy == 28
    assert manual_accuracy == 64
    assert manual_accuracy > 40


if __name__ == "__main__":
    main()
