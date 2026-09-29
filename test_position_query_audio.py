"""Focused unittest coverage for position-query audio preparation."""

from __future__ import annotations

import unittest
from unittest.mock import Mock

from position_query_audio import prepare_query_audio


class QueryAudioPreparationTests(unittest.TestCase):
    def test_enabled_audio_synthesizes_exactly_the_visible_response(self) -> None:
        response_text = "Casilla e4: peón blanco."
        synthesizer = Mock(return_value=(b"local-audio", "wav"))

        presentation = prepare_query_audio(
            response_text,
            "es",
            True,
            synthesizer,
        )

        self.assertEqual(presentation.text, response_text)
        self.assertEqual(presentation.audio_bytes, b"local-audio")
        self.assertEqual(presentation.audio_format, "wav")
        self.assertFalse(presentation.failed)
        synthesizer.assert_called_once_with(response_text, "es")

    def test_disabled_audio_keeps_text_without_calling_synthesizer(self) -> None:
        response_text = "Square e4: empty."
        synthesizer = Mock()

        presentation = prepare_query_audio(
            response_text,
            "en",
            False,
            synthesizer,
        )

        self.assertEqual(presentation.text, response_text)
        self.assertIsNone(presentation.audio_bytes)
        self.assertIsNone(presentation.audio_format)
        self.assertFalse(presentation.failed)
        synthesizer.assert_not_called()

    def test_synthesis_failure_keeps_complete_visible_text(self) -> None:
        response_text = "Position summary: 3 pieces."
        synthesizer = Mock(return_value=(None, None))

        presentation = prepare_query_audio(
            response_text,
            "en",
            True,
            synthesizer,
        )

        self.assertEqual(presentation.text, response_text)
        self.assertIsNone(presentation.audio_bytes)
        self.assertIsNone(presentation.audio_format)
        self.assertTrue(presentation.failed)
        synthesizer.assert_called_once_with(response_text, "en")


if __name__ == "__main__":
    unittest.main()
