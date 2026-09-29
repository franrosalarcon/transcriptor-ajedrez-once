"""Pure query engine over an immutable snapshot of a ``chess.Board``.

The engine never re-analyses images and never mutates the board it receives.
On entry it takes an immutable snapshot (a copy) of the board and answers the
query using python-chess APIs (:meth:`chess.Board.piece_at` and
:meth:`chess.Board.piece_map`).

Task 3.2 scope: combined filters (color + piece type + scope) applied jointly,
deterministic ``(rank, file)`` ordering (rank ascending, then file ``a``→``h``),
zero-result scopes that stay identifiable, and summary subtotals by color and
by piece type. Subtotals grouped by color always sum to the total.
"""

from __future__ import annotations

import chess

from position_query_models import (
    ParsedQuery,
    PieceMatch,
    QueryIntent,
    QueryResult,
)


def _snapshot(board: chess.Board) -> chess.Board:
    """Return an immutable-by-convention copy of ``board``.

    ``chess.Board.copy`` produces an independent board, so mutations performed
    while querying (if any) cannot reach the caller's board. The engine only
    reads from the snapshot, keeping the original FEN and turn intact.
    """

    return board.copy(stack=False)


def _in_scope(square: chess.Square, parsed: ParsedQuery) -> bool:
    """Return whether ``square`` satisfies the scope and filters jointly.

    Scope (square/rank/file) and filters (color/piece type) are intersected:
    a square only matches when it passes every constraint present on the query.
    Constraints left as ``None`` are ignored.
    """

    if parsed.square is not None and square != parsed.square:
        return False
    if parsed.rank is not None and chess.square_rank(square) != parsed.rank:
        return False
    if parsed.file is not None and chess.square_file(square) != parsed.file:
        return False
    return True


def _ordered_matches(snapshot: chess.Board, parsed: ParsedQuery) -> list[PieceMatch]:
    """Collect matching pieces ordered by rank ascending, then file ``a``→``h``.

    ``piece_map`` yields each occupied square exactly once, so results contain
    no duplicates. Color and piece-type filters are applied jointly with the
    scope before ordering.
    """

    matches: list[PieceMatch] = []
    for square, piece in snapshot.piece_map().items():
        if not _in_scope(square, parsed):
            continue
        if parsed.color is not None and piece.color != parsed.color:
            continue
        if parsed.piece_type is not None and piece.piece_type != parsed.piece_type:
            continue
        matches.append(
            PieceMatch(
                square=square,
                piece_type=piece.piece_type,
                color=piece.color,
            )
        )

    matches.sort(
        key=lambda m: (chess.square_rank(m.square), chess.square_file(m.square))
    )
    return matches


def _subtotals(
    matches: tuple[PieceMatch, ...]
) -> tuple[dict[chess.Color, int], dict[chess.PieceType, int]]:
    """Aggregate ``matches`` into color and piece-type subtotals.

    Each match contributes exactly one to its color bucket and one to its
    piece-type bucket, so both groupings independently sum to ``len(matches)``.
    """

    by_color: dict[chess.Color, int] = {}
    by_type: dict[chess.PieceType, int] = {}
    for match in matches:
        by_color[match.color] = by_color.get(match.color, 0) + 1
        by_type[match.piece_type] = by_type.get(match.piece_type, 0) + 1
    return by_color, by_type


def query(snapshot_source: chess.Board, parsed: ParsedQuery) -> QueryResult:
    """Answer ``parsed`` against an immutable snapshot of ``snapshot_source``.

    A snapshot is taken on entry so the caller's board is never mutated and no
    image analysis is repeated. The query is answered purely by reading the
    snapshot with python-chess APIs.

    For every intent the scope and any color/piece-type filters are applied
    jointly, matches are deduplicated and ordered by ``(rank, file)``, and
    color/piece-type subtotals are populated so that each grouping sums to the
    total. A valid query with no matches yields an empty match tuple while the
    :attr:`QueryResult.scope` still identifies what was queried.
    """

    snapshot = _snapshot(snapshot_source)

    # Scope + filters are applied jointly and the matches ordered/deduplicated
    # uniformly for every intent, including SUMMARY (which then reports the
    # subtotals below over the same occupied squares).
    matches = tuple(_ordered_matches(snapshot, parsed))

    by_color, by_type = _subtotals(matches)

    return QueryResult(
        scope=parsed,
        matches=matches,
        total=len(matches),
        by_color=by_color,
        by_type=by_type,
    )
