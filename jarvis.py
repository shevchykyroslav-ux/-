import asyncio
import os
import re
import subprocess
import sys
import time
import webbrowser
from datetime import datetime

import edge_tts
import pygame
import speech_recognition as sr
from faster_whisper import WhisperModel

# Импорт локального модуля brain
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import brain


# ============================================================
# НАСТРОЙКИ Программы
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

VOICE = "ru-RU-DmitryNeural"
MICROPHONE_INDEX = None  # None = автовыбор (или укажите номер, например 1, 2)
MODEL_SIZE = "small"

TEMP_AUDIO = os.path.join(BASE_DIR, "temp_audio.wav")
VOICE_FILE = os.path.join(BASE_DIR, "jarvis_voice.mp3")

CONVERSATION_TIMEOUT = 8  # Тайм-аут ожидания команд без повторного «Джарвис»


# ============================================================
# ИНИЦИАЛИЗАЦИЯ И ЗАГРУЗКА
# ============================================================

print("=" * 60)
print("                    J.A.R.V.I.S.")
print("=" * 60)

print("\nЗагрузка Whisper...")
print("Подождите...")

model = WhisperModel(
    MODEL_SIZE,
    device="cpu",
    compute_type="int8"
)

print("Whisper загружен.")

pygame.mixer.init()


# ============================================================
# ГОЛОСОВОЙ ДВИЖОК (TTS)
# ============================================================

async def generate_voice(text):
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(VOICE_FILE)


def speak(text):
    print(f"\nJARVIS: {text}")
    try:
        asyncio.run(generate_voice(text))

        pygame.mixer.music.stop()
        pygame.mixer.music.load(VOICE_FILE)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            time.sleep(0.03)

        pygame.mixer.music.unload()

    except Exception as e:
        print(f"Ошибка воспроизведения голоса: {e}")


# ============================================================
# НАСТРОЙКА МИКРОФОНА
# ============================================================

recognizer = sr.Recognizer()
recognizer.energy_threshold = 350
recognizer.dynamic_energy_threshold = True
recognizer.pause_threshold = 0.65
recognizer.phrase_threshold = 0.25
recognizer.non_speaking_duration = 0.3

print("\nКалибровка микрофона...")
try:
    with sr.Microphone(device_index=MICROPHONE_INDEX) as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
    print("Микрофон готов.")
except Exception as e:
        print(f"Ошибка инициализации микрофона: {e}")
        sys.exit()


# ============================================================
# ОБРАБОТКА И ФИЛЬТРАЦИЯ ТЕКСТА
# ============================================================

def normalize_text(text):
    text = text.lower().strip()
    text = re.sub(r"[^\w\sёа-яА-Я]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


NOISE_PHRASES = [
    "продолжение следует",
    "редактор субтитров",
    "редактор субтитров н",
    "добро пожаловать на наш канал",
    "пока добро пожаловать",
    "ставьте лайки",
    "подписывайтесь на канал",
    "подпишитесь на канал",
    "спасибо за просмотр"
]


def is_noise(text):
    if not text:
        return True
    text = normalize_text(text)
    if len(text) < 2:
        return True
    for phrase in NOISE_PHRASES:
        if phrase in text:
            return True
    return False


WAKE_WORDS = [
    "джарвис",
    "жарвис",
    "джарвес",
    "жарвес",
    "джар",
    "жар"
]


def contains_wake_word(text):
    text = normalize_text(text)
    for word in WAKE_WORDS:
        if word in text:
            return True
    return False


def remove_wake_word(text):
    text = normalize_text(text)
    for word in WAKE_WORDS:
        text = text.replace(word, "")
    return normalize_text(text)


# ============================================================
# ЗАПИСЬ И РАСПОЗНАВАНИЕ (LISTEN)
# ============================================================

def listen(timeout=5, phrase_time_limit=7):
    print("\n🎤 Слушаю...")
    try:
        with sr.Microphone(device_index=MICROPHONE_INDEX) as source:
            try:
                audio = recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
            except sr.WaitTimeoutError:
                return ""

        wav_data = audio.get_wav_data()
        with open(TEMP_AUDIO, "wb") as f:
            f.write(wav_data)

        print("🧠 Whisper распознаёт...")

        segments, info = model.transcribe(
            TEMP_AUDIO,
            language="ru",
            beam_size=5,
            best_of=3,
            vad_filter=True,
            vad_parameters={"min_silence_duration_ms": 400},
            condition_on_previous_text=False,
            temperature=0
        )

        text = " ".join(segment.text for segment in segments).strip()
        text = normalize_text(text)

        print(f"Whisper услышал: {text!r}")

        try:
            if os.path.exists(TEMP_AUDIO):
                os.remove(TEMP_AUDIO)
        except Exception:
            pass

        if is_noise(text):
            return ""

        return text

    except Exception as e:
        print(f"Ошибка распознавания: {e}")
        return ""


# ============================================================
# МЕТОДЫ УПРАВЛЕНИЯ ПРИЛОЖЕНИЯМИ И ОС
# ============================================================

def open_chrome():
    paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
    ]
    for path in paths:
        if os.path.exists(path):
            subprocess.Popen([path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return
    webbrowser.open("https://www.google.com")


def close_chrome():
    subprocess.run(["taskkill", "/IM", "chrome.exe", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def open_discord():
    try:
        os.startfile("discord://")
    except Exception:
        subprocess.Popen(["cmd", "/c", "start", "", "discord://"], shell=True)


def close_discord():
    subprocess.run(["taskkill", "/IM", "Discord.exe", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def open_steam():
    try:
        os.startfile("steam://open/main")
    except Exception:
        subprocess.Popen(["cmd", "/c", "start", "", "steam://open/main"], shell=True)


def close_steam():
    subprocess.run(["taskkill", "/IM", "steam.exe", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def open_cs2():
    os.startfile("steam://rungameid/730")


def open_youtube():
    webbrowser.open("https://www.youtube.com")


def open_google():
    webbrowser.open("https://www.google.com")


def lock_pc():
    subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])


# ============================================================
# КОМАНДНЫЙ ПРОЦЕССОР
# ============================================================

def process_command(command):
    command = normalize_text(command)

    print("\n" + "=" * 50)
    print(f"КОМАНДА: {command}")
    print("=" * 50)

    # 1. Chrome
    if "включи хром" in command or "открой хром" in command or "запусти хром" in command or "открой chrome" in command or "запусти chrome" in command:
        speak("Открываю Chrome.")
        open_chrome()
        return True

    if "закрой хром" in command or "выключи хром" in command or "закрой chrome" in command:
        speak("Закрываю Chrome.")
        close_chrome()
        return True

    # 2. Discord
    if "открой дискорд" in command or "запусти дискорд" in command or "включи дискорд" in command:
        speak("Открываю Discord.")
        open_discord()
        return True

    if "закрой дискорд" in command or "выключи дискорд" in command:
        speak("Закрываю Discord.")
        close_discord()
        return True

    # 3. Steam
    if "открой стим" in command or "запусти стим" in command or "включи стим" in command:
        speak("Открываю Steam.")
        open_steam()
        return True

    if "закрой стим" in command or "выключи стим" in command:
        speak("Закрываю Steam.")
        close_steam()
        return True

    # 4. CS2
    if "запусти кс" in command or "запусти кс 2" in command or "открой кс" in command or "включи контр страйк" in command:
        speak("Запускаю Counter-Strike 2.")
        open_cs2()
        return True

    # 5. YouTube & Google
    if "открой ютуб" in command or "запусти ютуб" in command or "включи ютуб" in command:
        speak("Открываю YouTube.")
        open_youtube()
        return True

    if "открой гугл" in command or "запусти гугл" in command:
        speak("Открываю Google.")
        open_google()
        return True

    # 6. Системные функции
    if "который час" in command or "сколько времени" in command or command == "время":
        current_time = datetime.now().strftime("%H:%M")
        speak(f"Сейчас {current_time}.")
        return True

    if command == "привет" or "как дела" in command:
        speak("Все системы работают штатно.")
        return True

    if "заблокируй компьютер" in command or "заблокируй пк" in command:
        speak("Блокирую компьютер.")
        time.sleep(0.4)
        lock_pc()
        return True

    if command in ["стоп", "остановись", "замолчи", "отмена"]:
        speak("Хорошо.")
        return True

    # 7. Запросы без совпадения отправляются в Ollama
    print("\n🧠 Передаю запрос в Brain...")
    answer = brain.ask_brain(command)
    speak(answer)
    return True


# ============================================================
# РЕЖИМ ДИАЛОГА (БЕЗ ПОВТОРНОГО "ДЖАРВИС")
# ============================================================

def conversation_mode():
    print("\n[ РЕЖИМ ДИАЛОГА АКТИВЕН ]")
    while True:
        command = listen(timeout=CONVERSATION_TIMEOUT, phrase_time_limit=7)
        if not command:
            print("\nДиалог завершён (тайм-аут).")
            return

        if contains_wake_word(command):
            command = remove_wake_word(command)

        if not command:
            continue

        process_command(command)


# ============================================================
# ОСНОВНОЙ ТОЧКА ВХОДА
# ============================================================

print("\n" + "=" * 60)
print("JARVIS ЗАПУЩЕН")
print("=" * 60)

try:
    while True:
        print("\n[ ОЖИДАНИЕ JARVIS ]")
        text = listen(timeout=5, phrase_time_limit=7)

        if not text:
            continue

        if not contains_wake_word(text):
            print("JARVIS не найден в речи.")
            continue

        command = remove_wake_word(text)

        if command:
            process_command(command)
            conversation_mode()
        else:
            print("\n🔔 JARVIS активирован. Ожидаю фразу...")
            command = listen(timeout=5, phrase_time_limit=7)
            if command:
                process_command(command)
                conversation_mode()

except KeyboardInterrupt:
    print("\n\nJARVIS выключен.")

except Exception as e:
    print(f"\nКритическая ошибка работы: {e}")

finally:
    try:
        pygame.mixer.music.stop()
        pygame.mixer.quit()
    except Exception:
        pass

    try:
        if os.path.exists(TEMP_AUDIO):
            os.remove(TEMP_AUDIO)
    except Exception:
        pass