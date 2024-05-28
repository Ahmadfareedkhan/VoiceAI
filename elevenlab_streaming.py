import os
from io import BytesIO
from typing import IO
from openai import OpenAI
from dotenv import load_dotenv
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
import simpleaudio as sa
from pydub import AudioSegment
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write




load_dotenv()

import time

def measure_latency(function, *args, **kwargs):
    start_time = time.time()
    result = function(*args, **kwargs)
    end_time = time.time()
    latency = end_time - start_time
    print(f"Latency of {function.__name__}: {latency:.2f} seconds")
    return result




# Setup OpenAI client
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

if not ELEVENLABS_API_KEY:
    raise ValueError("ELEVENLABS_API_KEY environment variable not set")

client = ElevenLabs(
    api_key=ELEVENLABS_API_KEY,
)


def record_audio(duration=5, sample_rate=44100):
    """
    Record audio from the microphone.
    """
    print("Recording...")
    recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=2, dtype='int16')
    sd.wait()  # Wait until recording is finished
    write('output.wav', sample_rate, recording)  # Save as WAV file
    print("Recording finished.")
    return 'output.wav'


def transcribe_audio(file_path):
    """
    Transcribe audio to text using OpenAI's Whisper model.
    """
    with open(file_path, "rb") as audio_file:
        transcription = openai_client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text"
        )
    # print("API Response:", transcription)  # Diagnostic print statement
    return transcription





def generate_response(user_input):
    """
    Generates a text response using OpenAI's GPT-3.5 Turbo model.

    Args:
        user_input (str): The user input text for which a response is needed.

    Returns:
        str: Generated response text.
    """
    completion = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        max_tokens=50,
        temperature=0.7,
        messages=[{"role": "system", "content": '''You are a conversational assistant named Eliza.
Use short, conversational responses as if you're having a live conversation.
Your response should be under 20 words.
Do not respond with any code, only conversation
do not repsond genereal knowledge information
work as a sale represenatative of company z360 which have CRM for businees mangement'''},
                  {"role": "user", "content": user_input}]
    )
    return completion.choices[0].message.content

def text_to_speech_stream(text: str) -> IO[bytes]:
    """
    Converts text to speech and returns the audio data as a byte stream.

    This function invokes a text-to-speech conversion API with specified parameters, including
    voice ID and various voice settings, to generate speech from the provided text. Instead of
    saving the output to a file, it streams the audio data into a BytesIO object.

    Args:
        text (str): The text content to be converted into speech.

    Returns:
        IO[bytes]: A BytesIO stream containing the audio data.
    """
    # Perform the text-to-speech conversion
    response = client.text_to_speech.convert(
        voice_id="21m00Tcm4TlvDq8ikWAM",  # Adam pre-made voice
        optimize_streaming_latency="0",
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_multilingual_v2",
        voice_settings=VoiceSettings(
            stability=0.0,
            similarity_boost=1.0,
            style=0.0,
            use_speaker_boost=True,
        ),
    )

    print("Streaming audio data...")

    # Create a BytesIO object to hold audio data
    audio_stream = BytesIO()

    # Write each chunk of audio data to the stream
    for chunk in response:
        if chunk:
            audio_stream.write(chunk)

    # Reset stream position to the beginning
    audio_stream.seek(0)


    # Convert MP3 to WAV using pydub
    mp3_audio = AudioSegment.from_file(audio_stream, format="mp3")
    wav_stream = BytesIO()
    mp3_audio.export(wav_stream, format="wav")
    wav_stream.seek(0)

    # Play the audio using simpleaudio
    wav_audio = wav_stream.read()
    play_obj = sa.play_buffer(wav_audio, num_channels=1, bytes_per_sample=2, sample_rate=22050)
    play_obj.wait_done()  # Wait until audio playback is finished

    print("Audio playback finished.")



if __name__ == "__main__":
    # Measure the latency of recording and transcribing audio
    audio_path = measure_latency(record_audio)
    transcript = measure_latency(transcribe_audio, audio_path)
    print("Transcript:", transcript)

    # If transcription is successful, generate and speak response
    if transcript.strip():  # Check if transcription was successful
        generated_text = measure_latency(generate_response, transcript)
        print("Generated Text:", generated_text)
        measure_latency(text_to_speech_stream, generated_text)
    else:
        print("No transcription available. Please try again.")