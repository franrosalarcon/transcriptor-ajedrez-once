"""Focused unittest suite for the pure position query engine (tasks 3.1-3.2).

Verifies snapshot immutability (original board FEN/turn intact), basic
square/rank/file lookups, jointly applied color/piece-type filters,
``(rank, file)`` ordering, zero-result scopes, and summary subtotals using
python-chess. Uses unittest because pytest is not installed in this
environment.
"""

from __future__ import annotations

import unittest

import chess

from position_query_engine import query
from position_query_models import ParsedQuery, PieceMatch, QueryIntent


class SquareQueryTests(unittest.TestCase):
    def test_occupied_square_returns_single_match(self) -> None:
        board = chess.Board()  # standard starting position
        parsed = ParsedQuery(intent=QueryIntent.SQUARE, square=chess.A1)

        result = query(board, parsed)

        self.assertEqual(result.total, 1)
        self.assertEqual(
            result.matches,
            (PieceMatch(square=chess.A1, piece_type=chess.ROOK, color=chess.WHITE),),
        )

    def test_empty_square_returns_no_matches(self) -> None:
        board = chess.Board()
        parsed = ParsedQuery(intent=QueryIntent.SQUARE, square=chess.E4)

        result = query(board, parsed)

        self.assertEqual(result.total, 0)
        self.assertEqual(result.matches, ())
        self.assertIs(result.scope, parsed)


class RankFileQueryTests(unittest.TestCase):
    def test_rank_lists_only_occupied_squares_on_that_rank(self) -> None:
        board = chess.Board()  # rank index 3 == rank "4" is empty at start
        parsed = ParsedQuery(intent=QueryIntent.RANK, rank=3)

        result = query(board, parsed)

        self.assertEqual(result.total, 0)

    def test_first_rank_has_eight_white_pieces(self) -> None:
        board = chess.Board()
        parsed = ParsedQuery(intent=QueryIntent.RANK, rank=0)

        result = query(board, parsed)

        self.assertEqual(result.total, 8)
        self.assertTrue(all(m.color == chess.WHITE for m in result.matches))
        self.assertTrue(all(chess.square_rank(m.square) == 0 for m in result.matches))

    def test_file_lists_both_ends(self) -> None:
        board = chess.Board()
        parsed = ParsedQuery(intent=QueryIntent.FILE, file=0)  # file "a"

        result = query(board, parsed)

        # a1, a2 (white) and a7, a8 (black) are occupied at the start.
        self.assertEqual(result.total, 4)
        self.assertTrue(all(chess.square_file(m.square) == 0 for m in result.matches))


class FilterOrderingAndSummaryTests(unittest.TestCase):
    def test_combined_scope_color_and_piece_type_filters_are_intersected(self) -> None:
        board = chess.Board(None)
        board.set_piece_at(chess.A1, chess.Piece(chess.ROOK, chess.WHITE))
        board.set_piece_at(chess.B1, chess.Piece(chess.QUEEN, chess.WHITE))
        board.set_piece_at(chess.C1, chess.Piece(chess.ROOK, chess.BLACK))
        board.set_piece_at(chess.D2, chess.Piece(chess.ROOK, chess.WHITE))
        parsed = ParsedQuery(
            intent=QueryIntent.FILTER,
            rank=0,
            color=chess.WHITE,
            piece_type=chess.ROOK,
        )

        result = query(board, parsed)

        self.assertEqual(
            result.matches,
            (PieceMatch(chess.A1, chess.ROOK, chess.WHITE),),
        )
        self.assertEqual(result.total, 1)
        self.assertEqual(dict(result.by_color), {chess.WHITE: 1})
        self.assertEqual(dict(result.by_type), {chess.ROOK: 1})

    def test_matches_are_unique_and_ordered_by_rank_then_file(self) -> None:
        board = chess.Board(None)
        placements = (
            (chess.A8, chess.BISHOP, chess.BLACK),
            (chess.C2, chess.KNIGHT, chess.WHITE),
            (chess.H1, chess.ROOK, chess.WHITE),
            (chess.A2, chess.PAWN, chess.WHITE),
            (chess.A1, chess.QUEEN, chess.WHITE),
        )
        for square, piece_type, color in placements:
            board.set_piece_at(square, chess.Piece(piece_type, color))

        result = query(board, ParsedQuery(intent=QueryIntent.FILTER))
        squares = tuple(match.square for match in result.matches)

        self.assertEqual(squares, (chess.A1, chess.H1, chess.A2, chess.C2, chess.A8))
        self.assertEqual(len(squares), len(set(squares)))

    def test_zero_matches_preserve_scope_and_have_empty_subtotals(self) -> None:
        board = chess.Board(None)
        board.set_piece_at(chess.H1, chess.Piece(chess.ROOK, chess.WHITE))
        parsed = ParsedQuery(
            intent=QueryIntent.FILTER,
            file=7,
            color=chess.BLACK,
            piece_type=chess.ROOK,
        )

        result = query(board, parsed)

        self.assertIs(result.scope, parsed)
        self.assertEqual(result.matches, ())
        self.assertEqual(result.total, 0)
        self.assertEqual(dict(result.by_color), {})
        self.assertEqual(dict(result.by_type), {})

    def test_summary_total_and_both_subtotal_groups_are_consistent(self) -> None:
        board = chess.Board(None)
        placements = (
            (chess.A1, chess.ROOK, chess.WHITE),
            (chess.B2, chess.PAWN, chess.WHITE),
            (chess.C6, chess.KNIGHT, chess.BLACK),
            (chess.H8, chess.ROOK, chess.BLACK),
        )
        for square, piece_type, color in placements:
            board.set_piece_at(square, chess.Piece(piece_type, color))

        result = query(board, ParsedQuery(intent=QueryIntent.SUMMARY))

        self.assertEqual(result.total, 4)
        self.assertEqual(dict(result.by_color), {chess.WHITE: 2, chess.BLACK: 2})
        self.assertEqual(
            dict(result.by_type),
            {chess.ROOK: 2, chess.PAWN: 1, chess.KNIGHT: 1},
        )
        self.assertEqual(sum(result.by_color.values()), result.total)
        self.assertEqual(sum(result.by_type.values()), result.total)


class NonMutationTests(unittest.TestCase):
    def test_engine_does_not_mutate_board_fen_or_turn(self) -> None:
        board = chess.Board()
        original_fen = board.fen()
        original_turn = board.turn

        query(board, ParsedQuery(intent=QueryIntent.SQUARE, square=chess.D1))
        query(board, ParsedQuery(intent=QueryIntent.RANK, rank=7))
        query(board, ParsedQuery(intent=QueryIntent.FILE, file=4))

        self.assertEqual(board.fen(), original_fen)
        self.assertEqual(board.turn, original_turn)

    def test_snapshot_is_independent_of_later_board_changes(self) -> None:
        board = chess.Board()
        parsed = ParsedQuery(intent=QueryIntent.SQUARE, square=chess.E2)

        result = query(board, parsed)
        board.push(chess.Move.from_uci("e2e4"))  # mutate after querying

        # The result captured the piece on e2 before the move.
        self.assertEqual(result.total, 1)
        self.assertEqual(result.matches[0].square, chess.E2)


if __name__ == "__main__":
    unittest.main()
