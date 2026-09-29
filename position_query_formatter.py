"""Pure localized text formatting for position-query domain outcomes.

The formatter is the single source of complete ES/EN response text for later
visible-output and TTS integration. It consumes only domain results produced by
the parser and engine: it never reads a board, reorders matches, or performs
image analysis.
"""

from __future__ import annotations

from typing import Literal, TypeAlias

import chess

from position_query_models import (
    Ambiguity,
    ControlError,
    ControlErrorCode,
    ParseError,
    ParseErrorCode,
    ParsedQuery,
    PieceMatch,
    QueryIntent,
    QueryResult,
)

Language = Literal["es", "en"]
FormattableOutcome: TypeAlias = QueryResult | ParseError | Ambiguity | ControlError

_PIECES_ES: dict[chess.PieceType, tuple[str, str, bool]] = {
    chess.PAWN: ("peón", "peones", False),
    chess.KNIGHT: ("caballo", "caballos", False),
    chess.BISHOP: ("alfil", "alfiles", False),
    chess.ROOK: ("torre", "torres", True),
    chess.QUEEN: ("dama", "damas", True),
    chess.KING: ("rey", "reyes", False),
}
_PIECES_EN: dict[chess.PieceType, tuple[str, str]] = {
    chess.PAWN: ("pawn", "pawns"),
    chess.KNIGHT: ("knight", "knights"),
    chess.BISHOP: ("bishop", "bishops"),
    chess.ROOK: ("rook", "rooks"),
    chess.QUEEN: ("queen", "queens"),
    chess.KING: ("king", "kings"),
}

_SUPPORTED_ES = (
    "Tipos disponibles: casilla, fila, columna, filtros por color o pieza y "
    "resumen. Ejemplo: \"torres blancas en la columna d\"."
)
_SUPPORTED_EN = (
    "Available query types: square, rank, file, color or piece filters, and "
    "summary. Example: \"white rooks on file d\"."
)


def _validate_language(lang: Language) -> None:
    if lang not in ("es", "en"):
        raise ValueError("lang must be 'es' or 'en'")


def _piece_name(piece_type: chess.PieceType, lang: Language, *, plural: bool) -> str:
    if lang == "es":
        names = _PIECES_ES[piece_type]
    else:
        names = _PIECES_EN[piece_type]
    return names[1 if plural else 0]


def _color_name(color: chess.Color, lang: Language) -> str:
    if lang == "es":
        return "blanco" if color == chess.WHITE else "negro"
    return "white" if color == chess.WHITE else "black"


def _describe_match(match: PieceMatch, lang: Language) -> str:
    square = chess.square_name(match.square)
    piece = _piece_name(match.piece_type, lang, plural=False)
    color = _color_name(match.color, lang)
    if lang == "es":
        feminine = _PIECES_ES[match.piece_type][2]
        if feminine:
            color = "blanca" if match.color == chess.WHITE else "negra"
        return f"{square}: {piece} {color}"
    return f"{square}: {color} {piece}"


def _describe_query(parsed: ParsedQuery, lang: Language) -> str:
    if parsed.intent == QueryIntent.SUMMARY:
        return "resumen" if lang == "es" else "summary"

    parts: list[str] = []
    if parsed.square is not None:
        name = chess.square_name(parsed.square)
        parts.append(f"casilla {name}" if lang == "es" else f"square {name}")
    if parsed.rank is not None:
        rank = parsed.rank + 1
        parts.append(f"fila {rank}" if lang == "es" else f"rank {rank}")
    if parsed.file is not None:
        file_name = chess.FILE_NAMES[parsed.file]
        parts.append(
            f"columna {file_name}" if lang == "es" else f"file {file_name}"
        )
    if not parts:
        parts.append("posición completa" if lang == "es" else "entire position")

    if parsed.color is not None:
        color = _color_name(parsed.color, lang)
        parts.append(f"color {color}")
    if parsed.piece_type is not None:
        piece = _piece_name(parsed.piece_type, lang, plural=False)
        parts.append(f"tipo {piece}" if lang == "es" else f"piece type {piece}")
    return ", ".join(parts)


def _format_summary(result: QueryResult, lang: Language) -> str:
    if lang == "es":
        noun = "pieza" if result.total == 1 else "piezas"
        colors = (
            f"blancas {result.by_color.get(chess.WHITE, 0)}, "
            f"negras {result.by_color.get(chess.BLACK, 0)}"
        )
        types = ", ".join(
            f"{_piece_name(piece_type, lang, plural=True)} "
            f"{result.by_type.get(piece_type, 0)}"
            for piece_type in chess.PIECE_TYPES
        )
        return (
            f"Resumen: {result.total} {noun}. Por color: {colors}. "
            f"Por tipo: {types}."
        )

    noun = "piece" if result.total == 1 else "pieces"
    colors = (
        f"white {result.by_color.get(chess.WHITE, 0)}, "
        f"black {result.by_color.get(chess.BLACK, 0)}"
    )
    types = ", ".join(
        f"{_piece_name(piece_type, lang, plural=True)} "
        f"{result.by_type.get(piece_type, 0)}"
        for piece_type in chess.PIECE_TYPES
    )
    return (
        f"Summary: {result.total} {noun}. By color: {colors}. "
        f"By type: {types}."
    )


def _format_result(result: QueryResult, lang: Language) -> str:
    scope = result.scope
    if scope.intent == QueryIntent.SUMMARY:
        return _format_summary(result, lang)

    if scope.intent == QueryIntent.SQUARE:
        if scope.square is None:
            raise ValueError("a square query must identify a square")
        square = chess.square_name(scope.square)
        if not result.matches:
            return (
                f"Casilla {square}: vacía."
                if lang == "es"
                else f"Square {square}: empty."
            )
        return (
            f"Casilla {_describe_match(result.matches[0], lang)}."
            if lang == "es"
            else f"Square {_describe_match(result.matches[0], lang)}."
        )

    if scope.intent in (QueryIntent.RANK, QueryIntent.FILE):
        description = _describe_query(scope, lang)
        heading = description[0].upper() + description[1:]
        if not result.matches:
            return (
                f"{heading}: sin piezas."
                if lang == "es"
                else f"{heading}: no occupied squares."
            )
        noun = (
            "pieza" if result.total == 1 else "piezas"
        ) if lang == "es" else ("piece" if result.total == 1 else "pieces")
        details = "; ".join(_describe_match(match, lang) for match in result.matches)
        return f"{heading}: {result.total} {noun}. {details}."

    description = _describe_query(scope, lang)
    if not result.matches:
        return (
            f"Sin coincidencias para {description}."
            if lang == "es"
            else f"No matches for {description}."
        )
    noun = (
        "coincidencia" if result.total == 1 else "coincidencias"
    ) if lang == "es" else ("match" if result.total == 1 else "matches")
    details = "; ".join(_describe_match(match, lang) for match in result.matches)
    if lang == "es":
        return f"Resultados para {description}: {result.total} {noun}. {details}."
    return f"Results for {description}: {result.total} {noun}. {details}."


def _format_error(error: ParseError, lang: Language) -> str:
    if error.code == ParseErrorCode.EMPTY_QUERY:
        prefix = "La consulta está vacía." if lang == "es" else "The query is empty."
    elif error.code == ParseErrorCode.UNSUPPORTED_QUERY:
        prefix = "Consulta no admitida." if lang == "es" else "Unsupported query."
    else:  # Defensive guard if the error enum grows without localized copy.
        raise ValueError(f"unsupported parse error code: {error.code!r}")
    return f"{prefix} {_SUPPORTED_ES if lang == 'es' else _SUPPORTED_EN}"


def _format_control_error(error: ControlError, lang: Language) -> str:
    if error.code == ControlErrorCode.NO_BOARD:
        if lang == "es":
            return (
                "No hay una posición analizada. "
                "Analiza un diagrama antes de consultar."
            )
        return (
            "There is no analyzed position. "
            "Analyze a diagram before querying."
        )
    if error.code == ControlErrorCode.INVALID_SELECTION:
        if lang == "es":
            return "Selección no válida. Elige uno de los índices disponibles."
        return "Invalid selection. Choose one of the available indices."
    raise ValueError(f"unsupported control error code: {error.code!r}")


def _format_ambiguity(ambiguity: Ambiguity, lang: Language) -> str:
    candidates = "; ".join(
        f"{index}) {_describe_query(candidate, lang)}"
        for index, candidate in enumerate(ambiguity.candidates, start=1)
    )
    if lang == "es":
        return (
            "La consulta tiene varias interpretaciones. "
            f"Selecciona una: {candidates}."
        )
    return f"The query has multiple interpretations. Select one: {candidates}."


def format_response(outcome: FormattableOutcome, lang: Language) -> str:
    """Return complete localized text for a query result, error, or ambiguity.

    Match order, counts, and subtotals are consumed exactly as supplied by the
    domain outcome. This function has no side effects and is suitable as the
    sole text source for both visible responses and later TTS integration.
    """

    _validate_language(lang)
    if isinstance(outcome, QueryResult):
        return _format_result(outcome, lang)
    if isinstance(outcome, ParseError):
        return _format_error(outcome, lang)
    if isinstance(outcome, Ambiguity):
        return _format_ambiguity(outcome, lang)
    if isinstance(outcome, ControlError):
        return _format_control_error(outcome, lang)
    raise TypeError(
        "outcome must be QueryResult, ParseError, Ambiguity, or ControlError"
    )
