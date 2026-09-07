```python
import pyautogui
import requests
import time
import os
import subprocess
import socket
import getpass
import ctypes
from datetime import datetime
import threading
import pystray
from PIL import Image, ImageDraw
import tkinter as tk
from tkinter import messagebox
import cv2


# ==========================
# Настройки соединения
# ==========================

REQUEST_TIMEOUT = 15
RECONNECT_DELAY = 5


# ==========================
# Telegram
# ==========================

try:
    folder = os.path.dirname(os.path.abspath(__file__))
    telegram_file = os.path.join(folder, "Telegram.txt")

    with open(telegram_file, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines()]

    BOT_TOKEN = lines[0]
    CHAT_ID = lines[1]

except Exception as e:
    print(f"Ошибка чтения Telegram.txt: {e}")
    os._exit(1)


# ==========================
# Данные ПК
# ==========================

PC_NAME = socket.gethostname()
USER_NAME = getpass.getuser()

START_TIME = time.time()

offset = None

# Состояние подключения
telegram_connected = False


# ==========================
# Telegram отправка
# ==========================

def telegram(text, keyboard=None):

    global telegram_connected

    data = {
        "chat_id": CHAT_ID,
        "text": text
    }

    if keyboard:
        data["reply_markup"] = {
            "keyboard": keyboard,
            "resize_keyboard": True
        }

    try:

        response = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json=data,
            timeout=REQUEST_TIMEOUT
        )

        response.raise_for_status()

        # Если до этого была потеря связи
        if not telegram_connected:

            telegram_connected = True

            print("🟢 Telegram connection restored")

        return True

    except requests.exceptions.RequestException as e:

        if telegram_connected:

            print(f"🔴 Telegram connection lost: {e}")

        else:

            print(f"⚠️ Telegram unavailable: {e}")

        telegram_connected = False

        return False

    except Exception as e:

        print(f"❌ Telegram error: {e}")

        telegram_connected = False

        return False


# ==========================
# Меню
# ==========================

def main_menu():

    keyboard = [
        [
            {"text": "📊 Статус"},
            {"text": "📷 Скриншот"}
        ],
        [
            {"text": "🔴 Выключить"},
            {"text": "🔄 Обновить"}
        ],
        [
            {"text": "📷 Камера"}
        ]
    ]

    return keyboard


# ==========================
# Статус
# ==========================

def get_uptime():

    sec = int(time.time() - START_TIME)

    return (
        f"{sec // 3600} ч "
        f"{(sec % 3600) // 60} мин"
    )


def status():

    telegram(
        f"💻 {PC_NAME}\n"
        f"👤 {USER_NAME}\n"
        f"⏱ {get_uptime()}\n"
        f"🕒 {datetime.now()}",
        main_menu()
    )


# ==========================
# Скриншот
# ==========================

def screenshot():

    try:

        import tempfile

        filename = os.path.join(
            tempfile.gettempdir(),
            "screen.png"
        )

        img = pyautogui.screenshot()

        img.save(filename)

        try:

            with open(
                filename,
                "rb"
            ) as photo:

                response = requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
                    data={
                        "chat_id": CHAT_ID,
                        "caption": f"📷 Скриншот {PC_NAME}"
                    },
                    files={
                        "photo": photo
                    },
                    timeout=REQUEST_TIMEOUT
                )

                response.raise_for_status()

        finally:

            if os.path.exists(filename):
                os.remove(filename)

    except requests.exceptions.RequestException as e:

        print(f"🔴 Ошибка отправки скриншота: {e}")

    except Exception as e:

        print(f"❌ Ошибка скриншота: {e}")


# ==========================
# Фото с камеры
# ==========================

def camera_photo():

    import tempfile

    try:

        cap = cv2.VideoCapture(0)

        if not cap.isOpened():

            telegram(
                "❌ Камера не найдена"
            )

            return

        ret, frame = cap.read()

        cap.release()

        if not ret:

            telegram(
                "❌ Не удалось получить изображение"
            )

            return

        filename = os.path.join(
            tempfile.gettempdir(),
            "camera_photo.jpg"
        )

        cv2.imwrite(
            filename,
            frame
        )

        try:

            with open(
                filename,
                "rb"
            ) as photo:

                response = requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
                    data={
                        "chat_id": CHAT_ID,
                        "caption":
                        f"📷 Фото с камеры\n"
                        f"💻 {PC_NAME}\n"
                        f"🕒 {datetime.now()}"
                    },
                    files={
                        "photo": photo
                    },
                    timeout=REQUEST_TIMEOUT
                )

                response.raise_for_status()

        finally:

            if os.path.exists(filename):
                os.remove(filename)

    except requests.exceptions.RequestException as e:

        print(f"🔴 Ошибка отправки фото: {e}")

    except Exception as e:

        print(f"❌ Ошибка камеры: {e}")


# ==========================
# Команды
# ==========================

def shutdown():

    telegram(
        f"🔴 {PC_NAME} выключается",
        main_menu()
    )

    os.system(
        "shutdown /s /f /t 30"
    )


def update_program():

    try:

        telegram(
            f"🔄 {PC_NAME}\n"
            f"Запуск обновления...",
            main_menu()
        )

        folder = os.path.dirname(
            os.path.abspath(__file__)
        )

        new_program = os.path.join(
            folder,
            "Launcher_1.1.pyw"
        )

        if os.path.exists(new_program):

            subprocess.Popen(
                [
                    "pythonw",
                    new_program
                ],
                cwd=folder
            )

            time.sleep(2)

            os._exit(0)

        else:

            telegram(
                "❌ Launcher_1.1.pyw не найден"
            )

    except Exception as e:

        print(f"❌ Ошибка обновления: {e}")


def lock():

    telegram(
        f"🔒 {PC_NAME} заблокирован",
        main_menu()
    )

    ctypes.windll.user32.LockWorkStation()


# ==========================
# Иконка в трее
# ==========================

def create_image():

    image = Image.new(
        "RGB",
        (64, 64),
        "black"
    )

    draw = ImageDraw.Draw(image)

    draw.rectangle(
        (16, 16, 48, 48),
        fill="green"
    )

    return image


def exit_program(icon, item):

    icon.stop()

    os._exit(0)


def tray():

    menu = pystray.Menu(
        pystray.MenuItem(
            "Выход",
            exit_program
        )
    )

    icon = pystray.Icon(
        "PC Control",
        create_image(),
        "PC Control",
        menu
    )

    icon.run()


threading.Thread(
    target=tray,
    daemon=True
).start()


# ==========================
# Получение старых сообщений
# ==========================

def initialize_offset():

    global offset

    try:

        response = requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates",
            timeout=REQUEST_TIMEOUT
        )

        response.raise_for_status()

        updates = response.json()

        if updates.get("result"):

            offset = (
                updates["result"][-1]["update_id"] + 1
            )

        print("🟢 Telegram initialization OK")

        return True

    except Exception as e:

        print(
            f"⚠️ Не удалось получить старые сообщения: {e}"
        )

        return False


# ==========================
# Основной цикл
# ==========================

print()
print("==============================")
print("   PC CONTROL STARTED")
print("==============================")
print(f"💻 PC: {PC_NAME}")
print(f"👤 User: {USER_NAME}")
print()


# ==========================
# Первоначальное подключение
# ==========================

connected_once = False

while not connected_once:

    print("🔄 Подключение к Telegram...")

    if telegram(
        f"🟢 ПК подключён\n\n"
        f"💻 {PC_NAME}\n"
        f"👤 {USER_NAME}",
        main_menu()
    ):

        connected_once = True

        print("🟢 Telegram connected")

    else:

        print(
            f"⏳ Нет интернета. "
            f"Повтор через {RECONNECT_DELAY} секунд..."
        )

        time.sleep(RECONNECT_DELAY)


# Пропускаем старые сообщения

initialize_offset()


# ==========================
# Главный цикл
# ==========================

while True:

    try:

        response = requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates",
            params={
                "offset": offset,
                "timeout": 30
            },
            timeout=40
        )

        response.raise_for_status()

        result = response.json()

        # Если после отключения интернет снова появился
        if not telegram_connected:

            telegram_connected = True

            print("🟢 Интернет / Telegram восстановлен")

            telegram(
                f"🟢 Связь восстановлена\n\n"
                f"💻 {PC_NAME}\n"
                f"👤 {USER_NAME}",
                main_menu()
            )

        # ==========================
        # Обработка сообщений
        # ==========================

        for upd in result.get("result", []):

            offset = upd["update_id"] + 1

            msg = upd.get(
                "message",
                {}
            )

            text = msg.get(
                "text",
                ""
            )

            sender = str(
                msg.get("chat", {})
                .get("id")
            )

            if sender != CHAT_ID:
                continue

            print(f"📩 Команда: {text}")

            if text == "📊 Статус":

                status()

            elif text == "📷 Скриншот":

                screenshot()

            elif text == "🔴 Выключить":

                shutdown()

            elif text == "🔄 Обновить":

                update_program()

            elif text == "📷 Камера":

                camera_photo()

    # ==========================
    # Потеря интернета
    # ==========================

    except requests.exceptions.Timeout:

        print(
            "⏳ Telegram timeout. "
            "Повторное подключение..."
        )

        telegram_connected = False

        time.sleep(RECONNECT_DELAY)

    except requests.exceptions.ConnectionError as e:

        print(
            f"🔴 Интернет отключён: {e}"
        )

        telegram_connected = False

        print(
            f"⏳ Повтор через {RECONNECT_DELAY} секунд..."
        )

        time.sleep(RECONNECT_DELAY)

    except requests.exceptions.RequestException as e:

        print(
            f"🔴 Ошибка Telegram: {e}"
        )

        telegram_connected = False

        time.sleep(RECONNECT_DELAY)

    except Exception as e:

        # Очень важно:
        # никакая ошибка не должна завершить программу

        print(
            f"⚠️ Ошибка основного цикла: {e}"
        )

        time.sleep(RECONNECT_DELAY)

    else:

        # Небольшая пауза между запросами
        time.sleep(2)
```
