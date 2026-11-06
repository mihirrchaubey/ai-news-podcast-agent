"""Multi-speaker podcast audio generation with Gemini TTS."""
import wave
from pathlib import Path
from typing import Dict

from google import genai
from google.adk.tools import ToolContext
from google.genai import types

from .. import config


def wave_file(filename, pcm, channels=1, rate=24000, sample_width=2):
    """Save raw PCM audio data as a WAV file."""
    with wave.open(str(filename), "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm)


async def generate_podcast_audio(
    podcast_script: str,
    tool_context: ToolContext,
    filename: str = "ai_today_podcast",
) -> Dict[str, str]:
    """
    Generates audio from a podcast script using the Gemini API and saves it as a WAV file.

    Args:
        podcast_script: The conversational script (speakers 'Joe' and 'Jane') to convert to audio.
        tool_context: The ADK tool context.
        filename: Base filename for the audio file (without extension).

    Returns:
        Dictionary with status and file information.
    """
    try:
        client = genai.Client()
        prompt = f"TTS the following conversation between Joe and Jane:\n\n{podcast_script}"

        speaker_configs = [
            types.SpeakerVoiceConfig(
                speaker=speaker,
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice)
                ),
            )
            for speaker, voice in config.HOST_VOICES.items()
        ]

        response = client.models.generate_content(
            model=config.TTS_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                        speaker_voice_configs=speaker_configs
                    )
                ),
            ),
        )

        data = response.candidates[0].content.parts[0].inline_data.data

        safe_name = Path(filename).name
        if not safe_name.endswith(".wav"):
            safe_name += ".wav"

        config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        file_path = config.OUTPUT_DIR / safe_name
        wave_file(file_path, data)

        return {
            "status": "success",
            "message": f"Successfully generated and saved podcast audio to {file_path.resolve()}",
            "file_path": str(file_path.resolve()),
            "file_size": len(data),
        }
    except Exception as e:
        return {"status": "error", "message": f"Audio generation failed: {str(e)[:200]}"}
