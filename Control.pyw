aimport pyautogui
import ctypes
import requests
import time
import os
import socket
import getpass
import ctypes
from datetime import datetime
import threading
import pystray
from PIL import Image, ImageDraw


# ==========================
# Telegram
# ==========================

BOT_TOKEN = "8695199400:AAEViIMPjk2NzDD4xigw_Aht2bczdMxPqaY"
CHAT_ID = "5182723934"


# ==========================
# Данные ПК
# ==========================

PC_NAME = socket.gethostname()
USER_NAME = getpass.getuser()

START_TIME = time.time()

offset = 0



# ==========================
# Отправка Telegram
# ==========================


def telegram(text, keyboard=None):

    data = {
        "chat_id": CHAT_ID,
        "text": text
    }

    if keyboard:
        data["reply_markup"] = {
            "keyboard": keyboard,
            "resize_keyboard": True
        }

    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json=data
    )



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
            {"text": "🔄 Перезагрузка"}
        ],
        [
            {"text": "🔒 Блокировать"}
        ]
    ]

    return keyboard



# ==========================
# Статус
# ==========================

def get_uptime():

    sec = int(time.time()-START_TIME)

    return (
        f"{sec//3600} ч "
        f"{(sec%3600)//60} мин"
    )



def status():

    telegram(
        f"💻 {PC_NAME}\n"
        f"👤 {USER_NAME}\n"
        f"⏱ {get_uptime()}\n"
        f"🕒 {datetime.now()}"
        ,
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



        with open(
            filename,
            "rb"
        ) as photo:

            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
                data={
                    "chat_id": CHAT_ID,
                    "caption": f"📷 Скриншот {PC_NAME}"
                },
                files={
                    "photo": photo
                }
            )


        os.remove(filename)


    except Exception as e:

        telegram(
            f"❌ Ошибка скриншота:\n{e}"
        )

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



def reboot():

    telegram(
        f"🔄 {PC_NAME} перезагрузка",
        main_menu()
    )

    os.system(
        "shutdown /r /f /t 30"
    )



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
        (64,64),
        "black"
    )

    draw = ImageDraw.Draw(image)

    draw.rectangle(
        (16,16,48,48),
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
# Запуск
# ==========================

telegram(
    f"🟢 ПК подключён\n\n"
    f"💻 {PC_NAME}\n"
    f"👤 {USER_NAME}",
    main_menu()
)



# ==========================
# Цикл
# ==========================

while True:

    try:

        result = requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates",
            params={
                "offset":offset,
                "timeout":30
            }
        ).json()


        for upd in result.get("result",[]):

            offset = upd["update_id"]+1


            msg = upd.get(
                "message",
                {}
            )


            text = msg.get(
                "text",
                ""
            )


            sender = str(
                msg.get("chat",{})
                .get("id")
            )


            if sender != CHAT_ID:
                continue



            if text=="📊 Статус":

                status()

            elif text=="📷 Скриншот":

                screenshot()


            elif text=="🔴 Выключить":

                shutdown()


            elif text=="🔄 Перезагрузка":

                reboot()


            elif text=="🔒 Блокировать":

                lock()



    except Exception as e:

        print(e)


    time.sleep(2)
