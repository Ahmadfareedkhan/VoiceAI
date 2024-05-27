import os
import uuid
from openai import OpenAI
from dotenv import load_dotenv
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs

# Load environment variables
load_dotenv('.env')

# Setup OpenAI client
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Setup ElevenLabs client
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
if not ELEVENLABS_API_KEY:
    raise ValueError("ELEVENLABS_API_KEY environment variable not set")
elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

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
        messages=[{"role": "user", "content": user_input}]
    )
    return completion.choices[0].message.content

def text_to_speech_file(text: str) -> str:
    """
    Converts text to speech and saves the output as an MP3 file.

    Args:
        text (str): The text content to convert to speech.

    Returns:
        str: The file path where the audio file has been saved.
    """
    response = elevenlabs_client.text_to_speech.convert(
        voice_id="pNInz6obpgDQGcFmaJgB",  # Example voice ID
        optimize_streaming_latency="0",
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_turbo_v2",  # Low latency model
        voice_settings=VoiceSettings(
            stability=0.0,
            similarity_boost=1.0,
            style=0.0,
            use_speaker_boost=True,
        ),
    )

    save_file_path = f"{uuid.uuid4()}.mp3"
    with open(save_file_path, "wb") as f:
        for chunk in response:
            if chunk:
                f.write(chunk)

    print(f"A new audio file was saved successfully at {save_file_path}")
    return save_file_path

if __name__ == "__main__":
    user_input = "Tell me about the latest advancements in AI technology."
    generated_text = generate_response(user_input)
    print("Generated Text:", generated_text)
    text_to_speech_file(generated_text)
