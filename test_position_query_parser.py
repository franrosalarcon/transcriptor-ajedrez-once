"""Focused unit tests for the bilingual position-query interpreter."""

import unittest

import chess

from position_query_models import (
    Ambiguity,
    ParseError,
    ParseErrorCode,
    ParsedQuery,
    QueryIntent,
)
from position_query_parser import parse


class PositionQueryParserTests(unittest.TestCase):
    def assert_bilingual_equivalent(
        self, spanish: str, english: str, expected: ParsedQuery
    ) -> None:
        self.assertEqual(parse(spanish, "es"), expected)
        self.assertEqual(parse(english, "en"), expected)

    def test_parses_square_queries_equally_in_spanish_and_english(self) -> None:
        self.assert_bilingual_equivalent(
            "¿Qué hay en E4?",
            "What is on e4?",
            ParsedQuery(QueryIntent.SQUARE, square=chess.E4),
        )

    def test_parses_file_queries_equally_in_spanish_and_english(self) -> None:
        self.assert_bilingual_equivalent(
            "qué piezas hay en la columna d",
            "what pieces are on file d",
            ParsedQuery(QueryIntent.FILE, file=chess.FILE_NAMES.index("d")),
        )

    def test_parses_rank_queries_equally_in_spanish_and_english(self) -> None:
        self.assert_bilingual_equivalent(
            "qué piezas hay en la fila 6",
            "what pieces are on rank 6",
            ParsedQuery(QueryIntent.RANK, rank=5),
        )

    def test_combines_color_piece_type_and_scope_filters(self) -> None:
        expected = ParsedQuery(
            QueryIntent.FILTER,
            file=3,
            color=chess.WHITE,
            piece_type=chess.KNIGHT,
        )

        self.assert_bilingual_equivalent(
            "caballos blancos en la columna d",
            "white knights on file d",
            expected,
        )

    def test_parses_piece_and_color_filters_without_a_scope(self) -> None:
        self.assert_bilingual_equivalent(
            "alfiles negros",
            "black bishops",
            ParsedQuery(
                QueryIntent.FILTER,
                color=chess.BLACK,
                piece_type=chess.BISHOP,
            ),
        )

    def test_parses_summary_queries_equally_in_both_languages(self) -> None:
        self.assert_bilingual_equivalent(
            "resumen de la posición",
            "position summary",
            ParsedQuery(QueryIntent.SUMMARY),
        )

    def test_returns_language_independent_errors(self) -> None:
        for lang in ("es", "en"):
            with self.subTest(lang=lang, case="empty"):
                self.assertEqual(
                    parse(" \t\n ", lang),
                    ParseError(ParseErrorCode.EMPTY_QUERY),
                )
            with self.subTest(lang=lang, case="unsupported"):
                self.assertEqual(
                    parse("consulta desconocida", lang),
                    ParseError(ParseErrorCode.UNSUPPORTED_QUERY),
                )

    def test_returns_language_independent_ambiguity_for_alternatives(self) -> None:
        expected = Ambiguity(
            (
                ParsedQuery(QueryIntent.SQUARE, square=chess.E4),
                ParsedQuery(QueryIntent.SQUARE, square=chess.D5),
            )
        )

        self.assertEqual(parse("qué hay en e4 o d5", "es"), expected)
        self.assertEqual(parse("what is on e4 or d5", "en"), expected)

    def test_rejects_unknown_language_codes(self) -> None:
        with self.assertRaisesRegex(ValueError, "lang"):
            parse("summary", "fr")


if __name__ == "__main__":
    unittest.main()
