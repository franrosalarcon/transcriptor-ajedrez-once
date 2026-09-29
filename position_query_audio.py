"""Pure local-audio preparation for position-query responses."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Literal, TypeAlias

Language: TypeAlias = Literal["es", "en"]
AudioSynthesizer: TypeAlias = Callable[
    [str, Language], tuple[bytes | None, str | None]
]


@dataclass(frozen=True, slots=True)
class QueryAudioPresentation:
    """Visible response text paired with optional locally synthesized audio."""

    text: str
    audio_bytes: bytes | None = None
    audio_format: str | None = None
    failed: bool = False


def prepare_query_audio(
    response_text: str,
    language: Language,
    audio_enabled: bool,
    synthesizer: AudioSynthesizer,
) -> QueryAudioPresentation:
    """Synthesize exactly the visible response when audio is explicitly enabled.

    Synthesis failures are converted to presentation state so callers can keep
    the complete text visible and display a localized warning.
    """

    if not audio_enabled:
        return QueryAudioPresentation(text=response_text)

    try:
        audio_bytes, audio_format = synthesizer(response_text, language)
    except Exception:
        return QueryAudioPresentation(text=response_text, failed=True)

    if not audio_bytes or not audio_format:
        return QueryAudioPresentation(text=response_text, failed=True)

    return QueryAudioPresentation(
        text=response_text,
        audio_bytes=audio_bytes,
        audio_format=audio_format,
    )
