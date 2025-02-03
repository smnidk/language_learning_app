from transformers import BlenderbotTokenizer, BlenderbotForConditionalGeneration, pipeline
import os
import json
import torch

# Настройка моделей
blenderbot_model_name = "facebook/blenderbot-400M-distill"
blenderbot_tokenizer = BlenderbotTokenizer.from_pretrained(blenderbot_model_name)
blenderbot_model = BlenderbotForConditionalGeneration.from_pretrained(blenderbot_model_name)

grammar_corrector_model = "vennify/t5-base-grammar-correction"
grammar_corrector = pipeline("text2text-generation", model=grammar_corrector_model)

translator = pipeline("translation", model="Helsinki-NLP/opus-mt-ru-en")  # Переводчик

# Константы
MAX_LENGTH = 1024
CHAT_HISTORY_FILE = "chat_history.json"


def load_chat_history():
    """Загрузить историю чата из файла."""
    if os.path.exists(CHAT_HISTORY_FILE):
        with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return []


def save_chat_history(chat_history):
    """Сохранить историю чата в файл."""
    with open(CHAT_HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(chat_history, file, ensure_ascii=False)


def translate_text(text, source_lang, target_lang):
    """Перевести текст с одного языка на другой."""
    try:
        if source_lang == "ru" and target_lang == "en":
            return translator(text)[0]["translation_text"]
        return text  # Если язык не поддерживается, возвращаем оригинальный текст
    except Exception as e:
        print(f"Ошибка перевода: {e}")
        return text


def correct_grammar(text):
    """Исправить грамматику текста."""
    try:
        return grammar_corrector(text, max_length=128)[0]['generated_text']
    except Exception as e:
        print(f"Ошибка исправления грамматики: {e}")
        return text


def generate_response(user_text, chat_history, user_language="ru"):
    """Сгенерировать ответ бота с использованием перевода и исправления грамматики."""
    try:
        # Перевод текста на английский
        if user_language != "en":
            user_text = translate_text(user_text, source_lang=user_language, target_lang="en")

        # Исправление грамматики
        corrected_text = correct_grammar(user_text)

        # Генерация ответа
        input_ids = blenderbot_tokenizer(corrected_text, return_tensors="pt", max_length=MAX_LENGTH, truncation=True)
        output_ids = blenderbot_model.generate(**input_ids)
        bot_response = blenderbot_tokenizer.decode(output_ids[0], skip_special_tokens=True).strip()

        # Перевод обратно на язык пользователя
        if user_language != "en":
            bot_response = translate_text(bot_response, source_lang="en", target_lang=user_language)

        # Сохранение в историю
        chat_history.append({"role": "user", "message": user_text})
        chat_history.append({"role": "bot", "message": bot_response})
        save_chat_history(chat_history)

        return bot_response

    except Exception as e:
        print(f"Ошибка в generate_response: {e}")
        return "Извините, произошла ошибка при генерации ответа."


# Основной код (отладка)
if __name__ == "__main__":
    chat_history = load_chat_history()

    while True:
        user_input = input("Вы: ")
        if user_input.lower() in ["выход", "exit", "quit"]:
            break

        response = generate_response(user_input, chat_history, user_language="ru")
        print(f"Бот: {response}")
