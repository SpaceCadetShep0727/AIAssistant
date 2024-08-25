#Libary imports
from openai import OpenAI
import os.path
from playsound import playsound
import speech_recognition as sr
import pyaudio

# Path to mp3 files for what we say and what the AI says
said_file_path = os.path.dirname(__file__) + '//said.wav'
response_file_path = os.path.dirname(__file__) + '//response.mp3'

# API Key
my_key = ''

# Connecting to OpenAI and initializing speech recognizer
client = OpenAI(api_key=my_key)
r = sr.Recognizer()
AI_name = 'Jarvis'
ready_for_command = True
print('Ready')
picture_wake_words = ['picture', 'image','photo']
voice_type = 'fable'

def get_audio():
  with sr.Microphone(device_index=1) as source:
    audio = r.listen(source)
    with open(said_file_path, 'wb') as file:
        file.write(audio.get_wav_data())

    try:
        said_file = open(said_file_path,'rb')
        transcription = client.audio.transcriptions.create(
            model = 'whisper-1',
            file = said_file
        )

        said = transcription.text
        print(said)
        global ready_for_command
        ready_for_command= False
        return said


    except sr.UnknownValueError:
        print('Error Listening')


def process_audio(said):
    global  ready_for_command
    if AI_name in said:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user",
                 "content": said}
            ]

        )
        text = completion.choices[0].message.content
        with client.audio.speech.with_streaming_response.create(

                model="tts-1",
                voice=voice_type,
                input=text

        ) as response:
            response.stream_to_file(response_file_path)

        playsound(response_file_path)
        print(text)
        os.remove(response_file_path) # deleting file
    ready_for_command = True


def create_image(said):
    global ready_for_command
    make_AI_say('Sure thing! I can make that for you, give me a second')
    image_prompt = said.split('of')
    response = client.images.generate(
        model="dall-e-3",
        prompt=image_prompt[1],
        size="1024x1024",
        quality="standard",
        n=1,

    )
    image_url = response.data[0].url
    print(image_url)
    ready_for_command = True

def make_AI_say(phrase):
    response_message = phrase
    with client.audio.speech.with_streaming_response.create(

            model="tts-1",
            voice=voice_type,
            input=response_message

    ) as response:
        response.stream_to_file(response_file_path)

    playsound(response_file_path)
    print(response_message)
    os.remove(response_file_path)  # deleting file

# Main function
while True:
    if ready_for_command:
        said = get_audio()
        if AI_name in said:
            if any(word in said for word in picture_wake_words):
                create_image(said)
            else:
                process_audio(said)


'''
Give project access to tts-1 model ( discuss tts-1) 
playsound ==1.2.2 
pyaudio
openAI
'''
