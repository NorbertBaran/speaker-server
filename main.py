import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from google.cloud import texttospeech
from fastapi.middleware.cors import CORSMiddleware
import yaml
from datetime import datetime

app = FastAPI()
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './speaker_credentials.json'
client = texttospeech.TextToSpeechClient()
origins = ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Speech(BaseModel):
    voice: str
    content: str


@app.get('/quota')
def quota(transfer: int = 0):
    if 0 <= transfer <= 250:
        with open('quota.yaml', 'r') as read_quota_file:
            quota = yaml.safe_load(read_quota_file)
        with open('quota.yaml', 'w') as write_quota_file:
            if quota['last_request_hour'] != datetime.now().hour:
                quota['last_request_hour'] = datetime.now().hour
                quota['transfer'] = 2000 - transfer
            else:
                quota['transfer'] = quota['transfer'] - transfer
            yaml.dump(quota, write_quota_file)
            return {'transfer': quota['transfer']}


@app.post('/speech')
async def speech(speech: Speech):
    synthesis_input = texttospeech.SynthesisInput({'text': speech.content})
    voice = texttospeech.VoiceSelectionParams({
        'language_code': speech.voice[:5],
        'name': speech.voice,
        'ssml_gender': texttospeech.SsmlVoiceGender.MALE
    })
    audio_config = texttospeech.AudioConfig({
        'audio_encoding': texttospeech.AudioEncoding.MP3
    })
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice,
        audio_config=audio_config
    )
    with open("audio.mp3", "wb") as out:
        out.write(response.audio_content)
        quota(len(speech.content))
    return FileResponse('audio.mp3')
