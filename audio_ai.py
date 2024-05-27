from openai import OpenAI
import requests
import os 
from dotenv import load_dotenv


load_dotenv('.env')
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

def generate_response(user_input):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        temperature=0.7,
        messages=[
            # {"role": "system", "content": proposal_template},
            {"role": "user", "content": user_input}
        ]
    )
    return completion.choices[0].message.content

def synthesize_speech(text, elevenlabs_api_key):
    """
    Convert text to speech using ElevenLabs API.
    """
    url = "https://api.elevenlabs.io/synthesize"
    headers = {
        "Authorization": f"Bearer {elevenlabs_api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "text": text,
         "voice": "en-US-Wavenet-A", # Optionally specify the voice model
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        with open('output.mp3', 'wb') as f:
            f.write(response.content)
        print("Speech synthesis complete, output saved as 'output.mp3'.")
    else:
        print("Failed to synthesize speech: ", response.text)

def main():
    # Replace with your actual API keys
    # OPENAI_API_KEY = "your_openai_api_key_here"
    ELEVENLABS_API_KEY = "f7f095d8f91be4f8d66d389046b7f673"

    # Example usage
    user_input = "Explain the concept of gravitational waves."
    generated_text = generate_response(user_input)
    print("Generated Text:", generated_text)
    synthesize_speech(generated_text, ELEVENLABS_API_KEY)

if __name__ == "__main__":
    main()
