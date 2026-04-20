from flask import Flask, request, jsonify
import requests
import re
import os
import json
from datetime import datetime

app = Flask(__name__)

PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN", "")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "quan123")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

ORDER_KEYWORDS = ["đặt", "mua", "order", "lấy", "chốt", "cho mình", "cho tôi", "book"]

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Lỗi Telegram: {e}")

def is_order_message(text):
    return any(k in text.lower() for k in ORDER_KEYWORDS)

def reply_messenger(sender_id, message):
    url = "https://graph.facebook.com/v18.0/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    payload = {
        "recipient": {"id": sender_id},
        "message": {"text": message},
        "messaging_type": "RESPONSE"
    }
    try:
        requests.post(url, params=params, json=payload)
    except Exception as e:
        print(f"Lỗi Messenger: {e}")

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if token == VERIFY_TOKEN:
            return challenge, 200
        return "Forbidden", 403

    data = request.json
    try:
        for entry in data.get("entry", []):
            for event in entry.get("messaging", []):
                sender_id = event["sender"]["id"]
                if "message" in event:
                    msg = event["message"]
                    if msg.get("is_echo"):
                        continue
                    text = msg.get("text", "")
                    if not text:
                        continue

                    if is_order_message(text):
                        phone_match = re.findall(r'(0[3-9][0-9]{8})', text)
                        phone = phone_match[0] if phone_match else "Chưa có SĐT"
                        time_now = datetime.now().strftime("%d/%m/%Y %H:%M")

                        tg_msg = (
                            f"🛒 <b>ĐƠN HÀNG MỚI!</b>\n\n"
                            f"⏰ {time_now}\n"
                            f"📱 SĐT: {phone}\n"
                            f"💬 Nội dung:\n<i>{text}</i>\n"
                            f"🆔 FB ID: {sender_id}"
                        )
                        send_telegram(tg_msg)
                        reply_messenger(sender_id,
                            "Cảm ơn bạn đã đặt hàng! 🎉 Shop sẽ liên hệ xác nhận trong 5-10 phút nhé!")
                    else:
                        reply_messenger(sender_id,
                            "Xin chào! 👋 Để đặt hàng, bạn nhắn:\n\"Đặt [sản phẩm] [số lượng] [SĐT]\"")
    except Exception as e:
        print(f"Lỗi: {e}")

    return jsonify({"status": "ok"}), 200

@app.route("/")
def index():
    return "Bot is running!", 200

if __name__ == "__main__":
    app.run(debug=False)
