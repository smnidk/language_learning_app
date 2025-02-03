import flet as ft
from chatbot import load_chat_history, save_chat_history, generate_response

def send_message(e, chat, input_box, page, chat_history):
    user_text = input_box.value.strip()
    if not user_text:
        return

    # Добавить сообщение пользователя в интерфейс
    chat_history.append({"role": "user", "message": user_text})
    chat.controls.append(
        ft.Row([ft.Container(ft.Text(user_text), bgcolor="#AEB8FE", padding=10, border_radius=8)], alignment="end")
    )
    input_box.value = ""
    page.update()

    # Генерация ответа
    try:
        bot_response = generate_response(user_text, chat_history, user_language="ru")  # Передаем язык
        chat_history.append({"role": "bot", "message": bot_response})

        # Добавить ответ бота в интерфейс
        chat.controls.append(
            ft.Row([ft.Container(ft.Text(bot_response), bgcolor="#FF8600", padding=10, border_radius=8)], alignment="start")
        )
        page.update()

        # Сохранить историю
        save_chat_history(chat_history)

    except Exception as e:
        print(f"Ошибка в send_message: {e}")
        chat.controls.append(
            ft.Row([ft.Container(ft.Text("Ошибка при обработке сообщения.", bgcolor="#FF0000", padding=10, border_radius=8))], alignment="start")
        )
        page.update()


def open_chat(page):
    page.title = "Chat with Bot"
    chat_history = load_chat_history()
    chat = ft.Column(scroll="always", expand=True)

    input_box = ft.TextField(
        hint_text="Введите сообщение...",
        expand=True,
        on_submit=lambda e: send_message(e, chat, input_box, page, chat_history)  # Передаем e
    )

    send_button = ft.IconButton(
        icon=ft.icons.SEND,
        on_click=lambda e: send_message(e, chat, input_box, page, chat_history),
        bgcolor="#FF8600",
        icon_color="white"
    )

    page.add(
        ft.Column(
            controls=[
                ft.Row(
                    [ft.Container(ft.Text("Чат-бот", color="white", size=20), bgcolor="#27187E", padding=15)],
                    alignment="spaceBetween",
                ),
                ft.Container(chat, expand=True, padding=10),
                ft.Row([input_box, send_button], alignment="spaceBetween"),
            ],
            expand=True,
        )
    )

    for message in chat_history:
        alignment = "end" if message["role"] == "user" else "start"
        bgcolor = "#AEB8FE" if message["role"] == "user" else "#FF8600"
        chat.controls.append(
            ft.Row([ft.Container(ft.Text(message["message"]), bgcolor=bgcolor, padding=10, border_radius=8)], alignment=alignment)
        )
    page.update()

def main(page: ft.Page):
    page.title = "Chatbot Menu"
    page.add(ft.ElevatedButton("Начать чат", on_click=lambda e: open_chat(page)))
    page.update()
