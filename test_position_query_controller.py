"""Focused unittest coverage for the pure position-query controller."""

from __future__ import annotations

import unittest
from unittest.mock import patch

import chess

from position_query_controller import select_ambiguity, submit_query
from position_query_formatter import format_response
from position_query_models import (
    Ambiguity,
    ControlError,
    ControlErrorCode,
    ParseError,
    ParseErrorCode,
    ParsedQuery,
    QueryIntent,
    QueryResult,
)


class SubmissionControlTests(unittest.TestCase):
    def test_missing_board_is_localized_without_parser_or_engine_calls(self) -> None:
        expected = {
            "es": (
                "No hay una posición analizada. "
                "Analiza un diagrama antes de consultar."
            ),
            "en": (
                "There is no analyzed position. "
                "Analyze a diagram before querying."
            ),
        }

        with (
            patch("position_query_controller.parse") as parser,
            patch("position_query_controller.query") as engine,
        ):
            for lang, text in expected.items():
                with self.subTest(lang=lang):
                    response = submit_query(None, "summary", lang)
                    self.assertEqual(
                        response.outcome,
                        ControlError(ControlErrorCode.NO_BOARD),
                    )
                    self.assertEqual(response.text, text)

            parser.assert_not_called()
            engine.assert_not_called()

    def test_parser_error_is_formatted_and_rejected_before_engine(self) -> None:
        error = ParseError(ParseErrorCode.UNSUPPORTED_QUERY)

        with (
            patch("position_query_controller.parse", return_value=error) as parser,
            patch("position_query_controller.query") as engine,
            patch(
                "position_query_controller.format_response",
                wraps=format_response,
            ) as formatter,
        ):
            response = submit_query(chess.Board(), "desconocida", "es")

        parser.assert_called_once_with("desconocida", "es")
        engine.assert_not_called()
        formatter.assert_called_once_with(error, "es")
        self.assertIs(response.outcome, error)
        self.assertTrue(response.text.startswith("Consulta no admitida."))

    def test_valid_query_uses_independent_snapshot_and_preserves_board(self) -> None:
        board = chess.Board()
        original_fen = board.fen()
        original_turn = board.turn
        parsed = ParsedQuery(QueryIntent.SQUARE, square=chess.E4)
        result = QueryResult(scope=parsed)
        received_snapshots: list[chess.Board] = []

        def execute(snapshot: chess.Board, selected: ParsedQuery) -> QueryResult:
            self.assertIs(selected, parsed)
            received_snapshots.append(snapshot)
            snapshot.clear()
            return result

        with (
            patch("position_query_controller.parse", return_value=parsed),
            patch("position_query_controller.query", side_effect=execute) as engine,
        ):
            response = submit_query(board, "e4", "en")

        engine.assert_called_once()
        self.assertIsNot(received_snapshots[0], board)
        self.assertEqual(board.fen(), original_fen)
        self.assertEqual(board.turn, original_turn)
        self.assertIs(response.outcome, result)
        self.assertEqual(response.text, "Square e4: empty.")

    def test_ambiguity_returns_candidates_without_engine_execution(self) -> None:
        ambiguity = Ambiguity(
            (
                ParsedQuery(QueryIntent.SQUARE, square=chess.E4),
                ParsedQuery(QueryIntent.SQUARE, square=chess.D5),
            )
        )

        with (
            patch("position_query_controller.parse", return_value=ambiguity),
            patch("position_query_controller.query") as engine,
        ):
            response = submit_query(chess.Board(), "e4 o d5", "es")

        engine.assert_not_called()
        self.assertIs(response.outcome, ambiguity)
        self.assertEqual(response.outcome.candidates, ambiguity.candidates)
        self.assertIn("Selecciona una: 1) casilla e4; 2) casilla d5.", response.text)


class AmbiguitySelectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.first = ParsedQuery(QueryIntent.SQUARE, square=chess.E4)
        self.second = ParsedQuery(QueryIntent.SQUARE, square=chess.D5)
        self.ambiguity = Ambiguity((self.first, self.second))

    def test_explicit_selection_executes_one_based_candidate_without_parsing(self) -> None:
        board = chess.Board()
        result = QueryResult(scope=self.second)

        with (
            patch("position_query_controller.parse") as parser,
            patch("position_query_controller.query", return_value=result) as engine,
        ):
            response = select_ambiguity(board, self.ambiguity, 2, "en")

        parser.assert_not_called()
        engine.assert_called_once()
        snapshot, selected = engine.call_args.args
        self.assertIsNot(snapshot, board)
        self.assertEqual(snapshot.fen(), board.fen())
        self.assertIs(selected, self.second)
        self.assertIs(response.outcome, result)
        self.assertEqual(response.text, "Square d5: empty.")

    def test_invalid_selection_is_controlled_and_never_executes_engine(self) -> None:
        with patch("position_query_controller.query") as engine:
            for invalid_index in (0, 3, -1, True, "1"):
                with self.subTest(selection_index=invalid_index):
                    response = select_ambiguity(
                        chess.Board(), self.ambiguity, invalid_index, "es"
                    )
                    self.assertEqual(
                        response.outcome,
                        ControlError(ControlErrorCode.INVALID_SELECTION),
                    )
                    self.assertEqual(
                        response.text,
                        "Selección no válida. "
                        "Elige uno de los índices disponibles.",
                    )

            engine.assert_not_called()


if __name__ == "__main__":
    unittest.main()
