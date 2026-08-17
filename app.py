import os
import html
import requests

from flask import Flask, render_template, request


app = Flask(__name__)


# =========================================================
# TELEGRAM
# =========================================================

TG_TOKEN = "8959526298:AAHOU35tjF6DWMzmRdxMoYAQHD-Rr3EvYiw"
TG_CHAT_ID = "5252390906"


# =========================================================
# HOME
# =========================================================

@app.route("/")
def index():
    return render_template("index.html")


# =========================================================
# SEND APPLICATION
# =========================================================

@app.route("/send", methods=["POST"])
def send():

    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    comment = request.form.get("comment", "").strip()
    lang = request.form.get("lang", "ru").strip().lower()

    # Проверяем язык
    if lang not in ("ru", "uz"):
        lang = "ru"

    # Значения по умолчанию
    if not name:
        name = "Не указано"

    if not phone:
        phone = "Не указано"

    if not comment:
        comment = "Нет комментария"


    # =====================================================
    # LOG
    # =====================================================

    print()
    print("========================================")
    print("НОВАЯ ЗАЯВКА")
    print("========================================")
    print("Имя:", name)
    print("Телефон:", phone)
    print("Комментарий:", comment)
    print("Язык:", lang)
    print("========================================")


    # =====================================================
    # TELEGRAM SETTINGS CHECK
    # =====================================================

    if not TG_TOKEN:

        print("❌ TG_TOKEN не найден")

        return render_template(
            "send.html",
            client_name=name,
            lang=lang,
            telegram_success=False,
            error_message="TG_TOKEN не настроен"
        ), 500


    if not TG_CHAT_ID:

        print("❌ TG_CHAT_ID не найден")

        return render_template(
            "send.html",
            client_name=name,
            lang=lang,
            telegram_success=False,
            error_message="TG_CHAT_ID не настроен"
        ), 500


    # =====================================================
    # ESCAPE USER DATA
    # =====================================================

    safe_name = html.escape(name)
    safe_phone = html.escape(phone)
    safe_comment = html.escape(comment)


    # =====================================================
    # TELEGRAM MESSAGE
    # =====================================================

    message = (
        "🎯 <b>Новая заявка на консультацию!</b>\n\n"
        f"👤 <b>Имя:</b> {safe_name}\n"
        f"📞 <b>Телефон:</b> {safe_phone}\n"
        f"💬 <b>Комментарий:</b> {safe_comment}"
    )


    # =====================================================
    # TELEGRAM API URL
    # =====================================================

    telegram_url = (
        f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    )


    payload = {
        "chat_id": TG_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }


    # =====================================================
    # SEND TO TELEGRAM
    # =====================================================

    try:

        response = requests.post(
            telegram_url,
            json=payload,
            timeout=15
        )


        print()
        print("========== TELEGRAM ==========")
        print("HTTP STATUS:", response.status_code)
        print("RESPONSE:", response.text)
        print("==============================")
        print()


        # -------------------------------------------------
        # HTTP ERROR
        # -------------------------------------------------

        if response.status_code != 200:

            return render_template(
                "send.html",
                client_name=name,
                lang=lang,
                telegram_success=False,
                error_message=f"Telegram HTTP {response.status_code}"
            ), 500


        # -------------------------------------------------
        # JSON
        # -------------------------------------------------

        try:
            data = response.json()

        except ValueError:

            print("❌ Telegram вернул неправильный JSON")

            return render_template(
                "send.html",
                client_name=name,
                lang=lang,
                telegram_success=False,
                error_message="Telegram вернул неправильный ответ"
            ), 500


        # -------------------------------------------------
        # TELEGRAM API ERROR
        # -------------------------------------------------

        if not data.get("ok"):

            description = data.get(
                "description",
                "Неизвестная ошибка Telegram"
            )

            print("❌ Telegram API:", description)

            return render_template(
                "send.html",
                client_name=name,
                lang=lang,
                telegram_success=False,
                error_message=description
            ), 500


        # =================================================
        # SUCCESS
        # =================================================

        print("✅ ЗАЯВКА УСПЕШНО ОТПРАВЛЕНА В TELEGRAM")


        return render_template(
            "send.html",
            client_name=name,
            lang=lang,
            telegram_success=True
        )


    except requests.RequestException as error:

        print()
        print("❌ ОШИБКА СОЕДИНЕНИЯ С TELEGRAM")
        print(error)
        print()


        return render_template(
            "send.html",
            client_name=name,
            lang=lang,
            telegram_success=False,
            error_message="Не удалось соединиться с Telegram"
        ), 500


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=8000,
        debug=True
    )