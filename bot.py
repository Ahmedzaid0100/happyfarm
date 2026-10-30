"""
🌾 Happy Farm - Official Telegram Bot Backend
Production-ready bot handler optimized for standard Python and cloud platforms (PythonAnywhere, Render, VPS).
"""

import os
import sys
import time
import json

# Attempt to use requests (pre-installed on PythonAnywhere and handles proxies automatically)
try:
    import requests
    USE_REQUESTS = True
except ImportError:
    USE_REQUESTS = False
    import urllib.request
    import urllib.parse

# ==================== CONFIGURATION ====================
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8627832293:AAGIjjF7V9dTKGRgTCHgM3127BF55--nz0k")
WEBAPP_URL = "https://ahmedzaid0100.github.io/happyfarm/"
CHANNEL_URL = "https://t.me/+hsG3joCzzOwxNTg0"

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# PythonAnywhere Proxy support for urllib fallback
PA_PROXY = os.getenv("http_proxy") or os.getenv("https_proxy") or "http://proxy.server:3128"

def api_request(method, data=None):
    url = f"{API_URL}/{method}"
    
    if USE_REQUESTS:
        try:
            if data:
                resp = requests.post(url, json=data, timeout=35)
            else:
                resp = requests.get(url, timeout=35)
            return resp.json()
        except Exception as e:
            print(f"API Error [{method}]: {e}")
            return None
    else:
        # Urllib fallback with proxy support
        try:
            proxy_support = urllib.request.ProxyHandler({'http': PA_PROXY, 'https': PA_PROXY})
            opener = urllib.request.build_opener(proxy_support)
            headers = {"Content-Type": "application/json"}
            body = json.dumps(data).encode("utf-8") if data else None
            req = urllib.request.Request(url, data=body, headers=headers)
            with opener.open(req, timeout=35) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as e:
            # Try without proxy if direct connection
            try:
                headers = {"Content-Type": "application/json"}
                body = json.dumps(data).encode("utf-8") if data else None
                req = urllib.request.Request(url, data=body, headers=headers)
                with urllib.request.urlopen(req, timeout=35) as response:
                    return json.loads(response.read().decode("utf-8"))
            except Exception as e2:
                print(f"API Error [{method}]: {e2}")
                return None

def send_welcome_message(chat_id, first_name, username):
    welcome_text = (
        f"👋 <b>أهلاً بك يا {first_name} في عالم مزرعة Crazy Farm!</b> 🌾\n\n"
        "🎮 <b>أقوى لعبة Web3 زراعية وقتالية على شبكة TON!</b>\n\n"
        "🌟 <b>مميزات اللعبة:</b>\n"
        "• 🐝 <b>مزرعة النحل:</b> تعدين مجاني فوري لنقاط FARM وتطوير مستواك.\n"
        "• 🐶 <b>سباق الجري RUN 3D:</b> تفادى العوائق واكسب عملات <b>CFC</b> كاش!\n"
        "• ⚔️ <b>حلبة قتال الحيوانات PVP:</b> معارك 3v3 و 5v5 و 7v7 وجوائز كبرى.\n"
        "• 💎 <b>سحب الأرباح:</b> تحويل فوري لعملات CFC على محفظة TON.\n\n"
        f"📢 <b>قناتنا الرسمية:</b> انضم لمتابعة التحديثات والجوائز:\n👉 {CHANNEL_URL}\n\n"
        "👇 <b>اضغط على الزر أدناه لبدء اللعب الآن مباشرة:</b>"
    )

    keyboard = {
        "inline_keyboard": [
            [
                {
                    "text": "🎮 العب الآن | Play Crazy Farm",
                    "web_app": {"url": WEBAPP_URL}
                }
            ],
            [
                {
                    "text": "📢 انضم للقناة الرسمية 🌾",
                    "url": CHANNEL_URL
                }
            ],
            [
                {
                    "text": "👥 دعوة الأصدقاء",
                    "switch_inline_query": "تعال العب معي في Crazy Farm واكسب عملات CFC مجاناً! 🌾"
                },
                {
                    "text": "❓ كيفية اللعب والربح",
                    "callback_data": "how_to_play"
                }
            ]
        ]
    }

    payload = {
        "chat_id": chat_id,
        "text": welcome_text,
        "parse_mode": "HTML",
        "reply_markup": keyboard
    }
    return api_request("sendMessage", payload)

def answer_callback(callback_query_id, text):
    payload = {
        "callback_query_id": callback_query_id,
        "text": text,
        "show_alert": True
    }
    return api_request("answerCallbackQuery", payload)

def set_bot_menu_button():
    payload = {
        "menu_button": {
            "type": "web_app",
            "text": "🌾 Play Farm",
            "web_app": {"url": WEBAPP_URL}
        }
    }
    res = api_request("setChatMenuButton", payload)
    if res and res.get("ok"):
        print("✅ Menu button set successfully to WebApp!")

def run_bot_polling():
    print("🚀 Starting Happy Farm Telegram Bot Polling...")
    set_bot_menu_button()
    
    offset = 0
    error_count = 0
    while True:
        try:
            updates_res = api_request("getUpdates", {"offset": offset, "timeout": 20})
            if updates_res and updates_res.get("ok"):
                error_count = 0
                for update in updates_res.get("result", []):
                    offset = update["update_id"] + 1

                    # Handle /start message
                    if "message" in update:
                        msg = update["message"]
                        chat_id = msg.get("chat", {}).get("id")
                        text = msg.get("text", "")
                        user = msg.get("from", {})
                        first_name = user.get("first_name", "Farmer")
                        username = user.get("username", "")

                        if text.startswith("/start"):
                            print(f"📥 /start from: {first_name} (@{username}, ID: {user.get('id')})")
                            send_welcome_message(chat_id, first_name, username)

                    # Handle Callback Queries
                    elif "callback_query" in update:
                        cb = update["callback_query"]
                        cb_id = cb.get("id")
                        data = cb.get("data")
                        if data == "how_to_play":
                            how_text = (
                                "🌾 طريقة اللعب والربح:\n"
                                "1. اجمع نقاط مزرعة النحل المجانية وطور مستواك.\n"
                                "2. العب سباق الجري RUN 3D بالكلب واكسب +50 CFC فوراً.\n"
                                "3. شارك في معارك الـ PVP واهزم الأعداء للحصول على جوائز إضافية.\n"
                                "4. اربط محفظة TON واسحب عملاتك إلى محفظتك في أي وقت!"
                            )
                            answer_callback(cb_id, how_text)
            else:
                error_count += 1
                if error_count > 3:
                    time.sleep(5)
                else:
                    time.sleep(1)

        except KeyboardInterrupt:
            print("\n🛑 Bot stopped by user.")
            break
        except Exception as e:
            print(f"Polling loop error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_bot_polling()
