"""Bilingual, language-independent interpreter for chess position queries."""

from __future__ import annotations

import itertools
import re
from collections.abc import Iterable
from typing import Literal, TypeAlias

import chess

from position_query_models import (
    Ambiguity,
    ParseError,
    ParseErrorCode,
    ParsedQuery,
    QueryIntent,
    normalize,
)

Language = Literal["es", "en"]
ParseOutcome: TypeAlias = ParsedQuery | Ambiguity | ParseError

_SUMMARY_WORDS: dict[Language, frozenset[str]] = {
    "es": frozenset({"resumen", "recuento"}),
    "en": frozenset({"summary", "count"}),
}

_COLOR_WORDS: dict[Language, dict[str, chess.Color]] = {
    "es": {
        "blanco": chess.WHITE,
        "blanca": chess.WHITE,
        "blancos": chess.WHITE,
        "blancas": chess.WHITE,
        "negro": chess.BLACK,
        "negra": chess.BLACK,
        "negros": chess.BLACK,
        "negras": chess.BLACK,
    },
    "en": {
        "white": chess.WHITE,
        "black": chess.BLACK,
    },
}

_PIECE_WORDS: dict[Language, dict[str, chess.PieceType]] = {
    "es": {
        "peón": chess.PAWN,
        "peones": chess.PAWN,
        "caballo": chess.KNIGHT,
        "caballos": chess.KNIGHT,
        "alfil": chess.BISHOP,
        "alfiles": chess.BISHOP,
        "torre": chess.ROOK,
        "torres": chess.ROOK,
        "dama": chess.QUEEN,
        "damas": chess.QUEEN,
        "reina": chess.QUEEN,
        "reinas": chess.QUEEN,
        "rey": chess.KING,
        "reyes": chess.KING,
    },
    "en": {
        "pawn": chess.PAWN,
        "pawns": chess.PAWN,
        "knight": chess.KNIGHT,
        "knights": chess.KNIGHT,
        "bishop": chess.BISHOP,
        "bishops": chess.BISHOP,
        "rook": chess.ROOK,
        "rooks": chess.ROOK,
        "queen": chess.QUEEN,
        "queens": chess.QUEEN,
        "king": chess.KING,
        "kings": chess.KING,
    },
}

_FILE_PATTERNS: dict[Language, re.Pattern[str]] = {
    "es": re.compile(r"\bcolumna\s+([a-h])\b"),
    "en": re.compile(r"\b(?:file|column)\s+([a-h])\b"),
}
_RANK_PATTERNS: dict[Language, re.Pattern[str]] = {
    "es": re.compile(r"\bfila\s+([1-8])\b"),
    "en": re.compile(r"\b(?:rank|row)\s+([1-8])\b"),
}
_SQUARE_PATTERN = re.compile(r"\b([a-h][1-8])\b")


def _words(text: str) -> tuple[str, ...]:
    """Split canonical text into words while discarding query punctuation."""

    return tuple(re.findall(r"[^\W_]+", text, flags=re.UNICODE))


def _unique(values: Iterable[int]) -> tuple[int, ...]:
    """Deduplicate values while retaining their order in the query."""

    return tuple(dict.fromkeys(values))


def _make_query(
    *,
    square: chess.Square | None = None,
    rank: int | None = None,
    file: int | None = None,
    color: chess.Color | None = None,
    piece_type: chess.PieceType | None = None,
) -> ParsedQuery:
    has_filter = color is not None or piece_type is not None
    if square is not None and not has_filter:
        intent = QueryIntent.SQUARE
    elif square is None and rank is not None and file is None and not has_filter:
        intent = QueryIntent.RANK
    elif square is None and file is not None and rank is None and not has_filter:
        intent = QueryIntent.FILE
    else:
        intent = QueryIntent.FILTER

    return ParsedQuery(
        intent=intent,
        square=square,
        rank=rank,
        file=file,
        color=color,
        piece_type=piece_type,
    )


def parse(text: str, lang: Language) -> ParseOutcome:
    """Interpret one Spanish or English position query.

    The returned objects contain chess values and error codes only; localization
    is deliberately left to the formatter. Multiple explicit alternatives (for
    example, two squares) are returned as an :class:`Ambiguity`.
    """

    if lang not in ("es", "en"):
        raise ValueError("lang must be 'es' or 'en'")

    canonical = normalize(text)
    if not canonical:
        return ParseError(ParseErrorCode.EMPTY_QUERY)

    words = _words(canonical)
    word_set = set(words)
    has_summary = bool(word_set & _SUMMARY_WORDS[lang])

    squares = tuple(
        chess.parse_square(name) for name in _unique(_SQUARE_PATTERN.findall(canonical))
    )
    files = _unique(
        ord(match) - ord("a") for match in _FILE_PATTERNS[lang].findall(canonical)
    )
    ranks = _unique(
        int(match) - 1 for match in _RANK_PATTERNS[lang].findall(canonical)
    )
    colors = _unique(
        _COLOR_WORDS[lang][word]
        for word in words
        if word in _COLOR_WORDS[lang]
    )
    piece_types = _unique(
        _PIECE_WORDS[lang][word]
        for word in words
        if word in _PIECE_WORDS[lang]
    )

    has_entities = bool(squares or files or ranks or colors or piece_types)
    if has_summary:
        if has_entities:
            return ParseError(ParseErrorCode.UNSUPPORTED_QUERY)
        return ParsedQuery(QueryIntent.SUMMARY)
    if not has_entities:
        return ParseError(ParseErrorCode.UNSUPPORTED_QUERY)

    square_options: tuple[chess.Square | None, ...] = squares or (None,)
    rank_options: tuple[int | None, ...] = ranks or (None,)
    file_options: tuple[int | None, ...] = files or (None,)
    color_options: tuple[chess.Color | None, ...] = colors or (None,)
    type_options: tuple[chess.PieceType | None, ...] = piece_types or (None,)

    candidates = tuple(
        dict.fromkeys(
            _make_query(
                square=square,
                rank=rank,
                file=file,
                color=color,
                piece_type=piece_type,
            )
            for square, rank, file, color, piece_type in itertools.product(
                square_options,
                rank_options,
                file_options,
                color_options,
                type_options,
            )
        )
    )
    if len(candidates) > 1:
        return Ambiguity(candidates)
    return candidates[0]
