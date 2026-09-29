"""Pure orchestration service for bilingual position queries.

This module coordinates parsing, immutable board snapshots, query execution,
and response formatting. It has no Streamlit, TTS, network, or persistence
concerns.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias

import chess

from position_query_engine import query
from position_query_formatter import format_response
from position_query_models import (
    Ambiguity,
    ControlError,
    ControlErrorCode,
    ParseError,
    ParsedQuery,
    QueryResult,
)
from position_query_parser import Language, parse

ControllerOutcome: TypeAlias = QueryResult | ParseError | Ambiguity | ControlError


@dataclass(frozen=True, slots=True)
class PositionQueryResponse:
    """A language-independent outcome paired with its complete visible text."""

    outcome: ControllerOutcome
    text: str


def _build_response(
    outcome: ControllerOutcome, lang: Language
) -> PositionQueryResponse:
    """Format an outcome once and return the service response."""

    return PositionQueryResponse(outcome=outcome, text=format_response(outcome, lang))


def _no_board_response(lang: Language) -> PositionQueryResponse:
    """Return the localized prerequisite error without parsing or querying."""

    return _build_response(ControlError(ControlErrorCode.NO_BOARD), lang)


def _snapshot(board: chess.Board) -> chess.Board:
    """Capture an independent board state at submission/selection time."""

    return board.copy(stack=False)


def submit_query(
    board: chess.Board | None,
    text: str,
    lang: Language,
) -> PositionQueryResponse:
    """Parse and execute one query against a submission-time snapshot.

    A missing board short-circuits before parsing. Parser errors and
    ambiguities short-circuit before engine execution. Valid parsed queries
    run against an independent copy, leaving the caller's board untouched.
    """

    if board is None:
        return _no_board_response(lang)

    parsed = parse(text, lang)
    if isinstance(parsed, (ParseError, Ambiguity)):
        return _build_response(parsed, lang)

    result = query(_snapshot(board), parsed)
    return _build_response(result, lang)


def select_ambiguity(
    board: chess.Board | None,
    ambiguity: Ambiguity,
    selection_index: int,
    lang: Language,
) -> PositionQueryResponse:
    """Execute a one-based candidate selection without parsing again.

    Invalid indexes (including booleans) produce a controlled localized
    outcome. A missing board still takes precedence and never reaches the
    engine.
    """

    if board is None:
        return _no_board_response(lang)

    if (
        isinstance(selection_index, bool)
        or not isinstance(selection_index, int)
        or not 1 <= selection_index <= len(ambiguity.candidates)
    ):
        return _build_response(
            ControlError(ControlErrorCode.INVALID_SELECTION), lang
        )

    selected = ambiguity.candidates[selection_index - 1]
    if not isinstance(selected, ParsedQuery):
        return _build_response(
            ControlError(ControlErrorCode.INVALID_SELECTION), lang
        )

    result = query(_snapshot(board), selected)
    return _build_response(result, lang)
