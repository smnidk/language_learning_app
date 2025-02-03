import flet as ft
import os

# Отключение предупреждения HF Hub
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

import chatbot  # Импорт после установки переменной
from ui import main

if __name__ == "__main__":
    ft.app(target=main)  # Flet передаст `page` автоматически
