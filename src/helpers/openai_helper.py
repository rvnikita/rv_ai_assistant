import openai
import os

# Ensure the OpenAI API key is loaded
client = openai.Client(api_key=os.getenv('ENV_OPENAI_KEY'))

def transcribe_audio(file_path):
    with open(file_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    return transcription.text

def generate_text(prompt):
    response = client.completion.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()
