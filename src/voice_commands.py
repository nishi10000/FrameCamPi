# voice_commands.py: 音声認識を通じてコマンドを受け取り、操作を行うモジュール

import speech_recognition as sr

listener = sr.Recognizer()

try:
    with sr.Microphone() as source:
        print("Listening...")
        voice = listener.listen(source)
        voice_text = listener.recognize_google(voice, language="ja-JP")
        print(voice_text)
except:
    print('Sorry, I could not listen')