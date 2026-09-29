"""Typed domain models for position queries.

The models in this module contain no parsing, formatting, persistence, or query
execution logic.  Chess coordinates use python-chess' zero-based indexes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Mapping

import chess


def normalize(text: str) -> str:
    """Return the canonical form used by position-query components.

    Leading and trailing whitespace is removed, internal whitespace runs are
    collapsed to one ASCII space, and Unicode-aware case folding is applied.
    """

    return " ".join(text.split()).casefold()


class QueryIntent(str, Enum):
    """Supported kinds of position query."""

    SQUARE = "square"
    RANK = "rank"
    FILE = "file"
    FILTER = "filter"
    SUMMARY = "summary"


class ParseErrorCode(str, Enum):
    """Language-independent reasons why a query cannot be parsed."""

    EMPTY_QUERY = "empty_query"
    UNSUPPORTED_QUERY = "unsupported_query"


class ControlErrorCode(str, Enum):
    """Language-independent failures produced by query orchestration."""

    NO_BOARD = "no_board"
    INVALID_SELECTION = "invalid_selection"


@dataclass(frozen=True, slots=True)
class ParsedQuery:
    """Structured query produced by the bilingual interpreter.

    ``square`` is in ``0..63``; ``rank`` and ``file`` are in ``0..7``.
    ``color`` and ``piece_type`` use python-chess values.
    """

    intent: QueryIntent
    square: chess.Square | None = None
    rank: int | None = None
    file: int | None = None
    color: chess.Color | None = None
    piece_type: chess.PieceType | None = None

    def __post_init__(self) -> None:
        if self.square is not None and (
            isinstance(self.square, bool) or not 0 <= self.square < 64
        ):
            raise ValueError("square must be a python-chess index from 0 to 63")
        if self.rank is not None and (
            isinstance(self.rank, bool) or not 0 <= self.rank < 8
        ):
            raise ValueError("rank must be a zero-based index from 0 to 7")
        if self.file is not None and (
            isinstance(self.file, bool) or not 0 <= self.file < 8
        ):
            raise ValueError("file must be a zero-based index from 0 to 7")
        if self.color is not None and not isinstance(self.color, bool):
            raise ValueError("color must be chess.WHITE or chess.BLACK")
        if self.piece_type is not None and (
            isinstance(self.piece_type, bool)
            or self.piece_type not in chess.PIECE_TYPES
        ):
            raise ValueError("piece_type must be a python-chess piece type")


@dataclass(frozen=True, slots=True)
class PieceMatch:
    """A unique piece matched by a query."""

    square: chess.Square
    piece_type: chess.PieceType
    color: chess.Color

    def __post_init__(self) -> None:
        if isinstance(self.square, bool) or not 0 <= self.square < 64:
            raise ValueError("square must be a python-chess index from 0 to 63")
        if (
            isinstance(self.piece_type, bool)
            or self.piece_type not in chess.PIECE_TYPES
        ):
            raise ValueError("piece_type must be a python-chess piece type")
        if not isinstance(self.color, bool):
            raise ValueError("color must be chess.WHITE or chess.BLACK")


@dataclass(frozen=True, slots=True)
class QueryResult:
    """Language-independent data returned by the query engine."""

    scope: ParsedQuery
    matches: tuple[PieceMatch, ...] = ()
    total: int = 0
    by_color: Mapping[chess.Color, int] = field(default_factory=dict)
    by_type: Mapping[chess.PieceType, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if isinstance(self.total, bool) or self.total < 0:
            raise ValueError("total must be a non-negative integer")
        if self.total != len(self.matches):
            raise ValueError("total must equal the number of matches")
        if any(isinstance(value, bool) or value < 0 for value in self.by_color.values()):
            raise ValueError("color subtotals must be non-negative integers")
        if any(isinstance(value, bool) or value < 0 for value in self.by_type.values()):
            raise ValueError("piece-type subtotals must be non-negative integers")

        object.__setattr__(self, "by_color", MappingProxyType(dict(self.by_color)))
        object.__setattr__(self, "by_type", MappingProxyType(dict(self.by_type)))


@dataclass(frozen=True, slots=True)
class Ambiguity:
    """Multiple valid interpretations that require a user selection."""

    candidates: tuple[ParsedQuery, ...]

    def __post_init__(self) -> None:
        if len(self.candidates) < 2:
            raise ValueError("an ambiguity must contain at least two candidates")


@dataclass(frozen=True, slots=True)
class ParseError:
    """Language-independent parse failure for later localized formatting."""

    code: ParseErrorCode


@dataclass(frozen=True, slots=True)
class ControlError:
    """Language-independent orchestration failure for localized formatting."""

    code: ControlErrorCode
