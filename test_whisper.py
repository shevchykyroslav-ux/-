from faster_whisper import WhisperModel
import speech_recognition as sr
import time

print("Загрузка Whisper...")

model = WhisperModel(
    "small",
    device="cpu",
    compute_type="int8"
)

print("Whisper загружен!")
print("Скажи что-нибудь...")

recognizer = sr.Recognizer()

with sr.Microphone() as source:
    recognizer.adjust_for_ambient_noise(source, duration=1)

    print("🎤 Говори:")
    audio = recognizer.listen(source, phrase_time_limit=6)

print("Распознаю...")

wav_data = audio.get_wav_data()

with open("test_audio.wav", "wb") as f:
    f.write(wav_data)

start = time.time()

segments, info = model.transcribe(
    "test_audio.wav",
    language="ru",
    beam_size=5
)

text = ""

for segment in segments:
    text += segment.text

print()
print("Ты сказал:", text.strip())
print("Время распознавания:", round(time.time() - start, 2), "сек.")