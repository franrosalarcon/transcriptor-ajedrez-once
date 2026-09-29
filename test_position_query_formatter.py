"""Focused unittest coverage for the pure localized response formatter."""

from __future__ import annotations

import unittest

import chess

from position_query_engine import query
from position_query_formatter import format_response
from position_query_models import (
    Ambiguity,
    ParseError,
    ParseErrorCode,
    ParsedQuery,
    PieceMatch,
    QueryIntent,
    QueryResult,
)


class SquareFormattingTests(unittest.TestCase):
    def test_formats_occupied_square_in_spanish_and_english(self) -> None:
        result = query(
            chess.Board(),
            ParsedQuery(QueryIntent.SQUARE, square=chess.A1),
        )

        self.assertEqual(format_response(result, "es"), "Casilla a1: torre blanca.")
        self.assertEqual(format_response(result, "en"), "Square a1: white rook.")

    def test_formats_empty_square_in_spanish_and_english(self) -> None:
        result = query(
            chess.Board(),
            ParsedQuery(QueryIntent.SQUARE, square=chess.E4),
        )

        self.assertEqual(format_response(result, "es"), "Casilla e4: vacía.")
        self.assertEqual(format_response(result, "en"), "Square e4: empty.")


class ScopeAndFilterFormattingTests(unittest.TestCase):
    def test_formats_rank_and_preserves_match_order_from_result(self) -> None:
        scope = ParsedQuery(QueryIntent.RANK, rank=0)
        result = QueryResult(
            scope=scope,
            matches=(
                PieceMatch(chess.C1, chess.BISHOP, chess.BLACK),
                PieceMatch(chess.A1, chess.ROOK, chess.WHITE),
            ),
            total=2,
        )

        self.assertEqual(
            format_response(result, "es"),
            "Fila 1: 2 piezas. c1: alfil negro; a1: torre blanca.",
        )
        self.assertEqual(
            format_response(result, "en"),
            "Rank 1: 2 pieces. c1: black bishop; a1: white rook.",
        )

    def test_formats_file_and_identifies_empty_scope(self) -> None:
        result = query(
            chess.Board(None),
            ParsedQuery(QueryIntent.FILE, file=chess.FILE_NAMES.index("d")),
        )

        self.assertEqual(format_response(result, "es"), "Columna d: sin piezas.")
        self.assertEqual(
            format_response(result, "en"),
            "File d: no occupied squares.",
        )

    def test_formats_joint_filters_and_result_details(self) -> None:
        board = chess.Board(None)
        board.set_piece_at(chess.A1, chess.Piece(chess.ROOK, chess.WHITE))
        result = query(
            board,
            ParsedQuery(
                QueryIntent.FILTER,
                rank=0,
                color=chess.WHITE,
                piece_type=chess.ROOK,
            ),
        )

        self.assertEqual(
            format_response(result, "es"),
            "Resultados para fila 1, color blanco, tipo torre: 1 coincidencia. "
            "a1: torre blanca.",
        )
        self.assertEqual(
            format_response(result, "en"),
            "Results for rank 1, color white, piece type rook: 1 match. "
            "a1: white rook.",
        )

    def test_zero_filter_results_identify_complete_scope_and_filters(self) -> None:
        result = query(
            chess.Board(None),
            ParsedQuery(
                QueryIntent.FILTER,
                file=7,
                color=chess.BLACK,
                piece_type=chess.ROOK,
            ),
        )

        self.assertEqual(
            format_response(result, "es"),
            "Sin coincidencias para columna h, color negro, tipo torre.",
        )
        self.assertEqual(
            format_response(result, "en"),
            "No matches for file h, color black, piece type rook.",
        )


class SummaryFormattingTests(unittest.TestCase):
    def test_formats_total_and_all_color_and_type_subtotals(self) -> None:
        board = chess.Board(None)
        for square, piece_type, color in (
            (chess.A1, chess.ROOK, chess.WHITE),
            (chess.B2, chess.PAWN, chess.WHITE),
            (chess.C6, chess.KNIGHT, chess.BLACK),
            (chess.H8, chess.ROOK, chess.BLACK),
        ):
            board.set_piece_at(square, chess.Piece(piece_type, color))
        result = query(board, ParsedQuery(QueryIntent.SUMMARY))

        self.assertEqual(
            format_response(result, "es"),
            "Resumen: 4 piezas. Por color: blancas 2, negras 2. Por tipo: "
            "peones 1, caballos 1, alfiles 0, torres 2, damas 0, reyes 0.",
        )
        self.assertEqual(
            format_response(result, "en"),
            "Summary: 4 pieces. By color: white 2, black 2. By type: "
            "pawns 1, knights 1, bishops 0, rooks 2, queens 0, kings 0.",
        )


class ErrorAndAmbiguityFormattingTests(unittest.TestCase):
    def test_formats_empty_and_unsupported_errors_with_types_and_example(self) -> None:
        cases = (
            (
                ParseError(ParseErrorCode.EMPTY_QUERY),
                "La consulta está vacía. Tipos disponibles: casilla, fila, columna, "
                "filtros por color o pieza y resumen. Ejemplo: \"torres blancas en "
                "la columna d\".",
                "The query is empty. Available query types: square, rank, file, "
                "color or piece filters, and summary. Example: \"white rooks on "
                "file d\".",
            ),
            (
                ParseError(ParseErrorCode.UNSUPPORTED_QUERY),
                "Consulta no admitida. Tipos disponibles: casilla, fila, columna, "
                "filtros por color o pieza y resumen. Ejemplo: \"torres blancas en "
                "la columna d\".",
                "Unsupported query. Available query types: square, rank, file, "
                "color or piece filters, and summary. Example: \"white rooks on "
                "file d\".",
            ),
        )

        for error, spanish, english in cases:
            with self.subTest(code=error.code, lang="es"):
                self.assertEqual(format_response(error, "es"), spanish)
            with self.subTest(code=error.code, lang="en"):
                self.assertEqual(format_response(error, "en"), english)

    def test_formats_ambiguity_with_localized_candidate_descriptions(self) -> None:
        ambiguity = Ambiguity(
            (
                ParsedQuery(QueryIntent.SQUARE, square=chess.E4),
                ParsedQuery(
                    QueryIntent.FILTER,
                    file=3,
                    color=chess.WHITE,
                    piece_type=chess.KNIGHT,
                ),
            )
        )

        self.assertEqual(
            format_response(ambiguity, "es"),
            "La consulta tiene varias interpretaciones. Selecciona una: "
            "1) casilla e4; 2) columna d, color blanco, tipo caballo.",
        )
        self.assertEqual(
            format_response(ambiguity, "en"),
            "The query has multiple interpretations. Select one: "
            "1) square e4; 2) file d, color white, piece type knight.",
        )

    def test_rejects_unknown_languages_and_outcome_types(self) -> None:
        with self.assertRaisesRegex(ValueError, "lang"):
            format_response(ParseError(ParseErrorCode.EMPTY_QUERY), "fr")
        with self.assertRaisesRegex(TypeError, "outcome"):
            format_response(object(), "es")


if __name__ == "__main__":
    unittest.main()
