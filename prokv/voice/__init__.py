"""Local Russian text-to-speech (Silero TTS) for voiceover tracks."""

from prokv.voice.silero import DEFAULT_VOICE, VOICES, SileroTTS, VoiceConfig, wav_duration

from prokv.voice.narration import Narration, narrate_episode  # noqa: E402

__all__ = ["DEFAULT_VOICE", "VOICES", "Narration", "SileroTTS", "VoiceConfig", "narrate_episode", "wav_duration"]
