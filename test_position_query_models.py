"""Unit tests for the position-query domain models."""

import unittest
from dataclasses import FrozenInstanceError

import chess

from position_query_models import (
    Ambiguity,
    ParseError,
    ParseErrorCode,
    ParsedQuery,
    PieceMatch,
    QueryIntent,
    QueryResult,
    normalize,
)


class PositionQueryNormalizationTests(unittest.TestCase):
    def test_normalize_trims_collapses_whitespace_and_ignores_case(self) -> None:
        self.assertEqual(normalize("  QuÉ\tPIEZA\n  EN   E4  "), "qué pieza en e4")

    def test_normalize_uses_unicode_casefold(self) -> None:
        self.assertEqual(normalize("  STRASSE  "), normalize("Straße"))

    def test_normalize_is_idempotent(self) -> None:
        normalized = normalize("  QUÉ   hay\tEN A1? ")

        self.assertEqual(normalize(normalized), normalized)


class PositionQueryModelsTests(unittest.TestCase):
    def test_parsed_query_holds_scope_and_joint_filters(self) -> None:
        query = ParsedQuery(
            intent=QueryIntent.FILTER,
            rank=3,
            file=2,
            color=chess.WHITE,
            piece_type=chess.KNIGHT,
        )

        self.assertEqual(query.rank, 3)
        self.assertEqual(query.file, 2)
        self.assertEqual(query.color, chess.WHITE)
        self.assertEqual(query.piece_type, chess.KNIGHT)

    def test_piece_match_uses_python_chess_values_and_is_immutable(self) -> None:
        match = PieceMatch(chess.E4, chess.PAWN, chess.BLACK)

        self.assertEqual(
            (match.square, match.piece_type, match.color),
            (chess.E4, chess.PAWN, chess.BLACK),
        )
        with self.assertRaises(FrozenInstanceError):
            match.square = chess.E5

    def test_parsed_query_rejects_invalid_chess_indexes(self) -> None:
        invalid_values = (
            ("square", 64),
            ("rank", 8),
            ("file", -1),
            ("piece_type", 7),
        )

        for field_name, value in invalid_values:
            with self.subTest(field=field_name, value=value):
                with self.assertRaises(ValueError):
                    ParsedQuery(QueryIntent.FILTER, **{field_name: value})

    def test_query_result_keeps_typed_matches_and_read_only_subtotals(self) -> None:
        scope = ParsedQuery(QueryIntent.SUMMARY)
        matches = (
            PieceMatch(chess.A1, chess.ROOK, chess.WHITE),
            PieceMatch(chess.H8, chess.KING, chess.BLACK),
        )
        result = QueryResult(
            scope=scope,
            matches=matches,
            total=2,
            by_color={chess.WHITE: 1, chess.BLACK: 1},
            by_type={chess.ROOK: 1, chess.KING: 1},
        )

        self.assertIs(result.scope, scope)
        self.assertEqual(result.matches, matches)
        self.assertEqual(sum(result.by_color.values()), result.total)
        self.assertEqual(sum(result.by_type.values()), result.total)
        with self.assertRaises(TypeError):
            result.by_color[chess.WHITE] = 2

    def test_query_result_rejects_an_inconsistent_total(self) -> None:
        match = PieceMatch(chess.A1, chess.ROOK, chess.WHITE)

        with self.assertRaisesRegex(ValueError, "total must equal"):
            QueryResult(ParsedQuery(QueryIntent.SUMMARY), (match,), total=0)

    def test_ambiguity_requires_multiple_typed_candidates(self) -> None:
        candidates = (
            ParsedQuery(QueryIntent.FILE, file=0),
            ParsedQuery(QueryIntent.SQUARE, square=chess.A1),
        )

        self.assertEqual(Ambiguity(candidates).candidates, candidates)
        with self.assertRaisesRegex(ValueError, "at least two"):
            Ambiguity(candidates[:1])

    def test_parse_error_is_language_independent_and_typed(self) -> None:
        error = ParseError(ParseErrorCode.UNSUPPORTED_QUERY)

        self.assertIs(error.code, ParseErrorCode.UNSUPPORTED_QUERY)
        self.assertFalse(hasattr(error, "message"))


if __name__ == "__main__":
    unittest.main()
