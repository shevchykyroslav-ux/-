import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:3b"

SYSTEM_PROMPT = (
    "Ты — J.A.R.V.I.S., искусственный интеллект и личный помощник. "
    "Отвечай коротко, четко, вежливо и по делу. Максимум 1-2 предложения."
)

def ask_brain(prompt: str) -> str:
    try:
        payload = {
            "model": MODEL_NAME,
            "prompt": f"{SYSTEM_PROMPT}\n\nПользователь: {prompt}\nJ.A.R.V.I.S.:",
            "stream": False,
            "options": {
                "temperature": 0.6,
                "num_predict": 100
            }
        }
        
        response = requests.post(OLLAMA_URL, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json().get("response", "").strip()
            return result if result else "Я затрудняюсь ответить."
        else:
            return "Ошибка связи с локальным ядром."

    except Exception:
        return "Мой нейронный модуль временно недоступен. Проверьте запуск Ollama."