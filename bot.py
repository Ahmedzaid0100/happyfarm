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
    session = requests.Session()
    # Explicitly ensure environment proxies are used
    session.trust_env = True
except ImportError:
    USE_REQUESTS = False
    session = None
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
    
    if USE_REQUESTS and session:
        for attempt in range(2):
            try:
                if data:
                    resp = session.post(url, json=data, timeout=15)
                else:
                    resp = session.get(url, timeout=15)
                
                if resp.status_code == 200:
                    return resp.json()
                elif resp.status_code == 409:
                    print("⚠️ Telegram 409 Conflict: Bot running in another location.")
                    time.sleep(4)
                    return None
                else:
                    time.sleep(2)
            except Exception as e:
                err_str = str(e)
                if "503" in err_str or "Proxy" in err_str or "Tunnel" in err_str:
                    # Proxy blip on PythonAnywhere - silent backoff
                    time.sleep(3)
                else:
                    print(f"API Error [{method}]: {e}")
                    time.sleep(2)
        return None
    else:
        # Urllib fallback with proxy support
        try:
            proxy_support = urllib.request.ProxyHandler({'http': PA_PROXY, 'https': PA_PROXY})
            opener = urllib.request.build_opener(proxy_support)
            headers = {"Content-Type": "application/json"}
            body = json.dumps(data).encode("utf-8") if data else None
            req = urllib.request.Request(url, data=body, headers=headers)
            with opener.open(req, timeout=15) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as e:
            # Try without proxy if direct connection
            try:
                headers = {"Content-Type": "application/json"}
                body = json.dumps(data).encode("utf-8") if data else None
                req = urllib.request.Request(url, data=body, headers=headers)
                with urllib.request.urlopen(req, timeout=15) as response:
                    return json.loads(response.read().decode("utf-8"))
            except Exception as e2:
                time.sleep(2)
                return None

def send_welcome_message(chat_id, first_name, username):
    welcome_text = (
        f"👋 <b>أهلاً بك يا {first_name} في عالم مزرعة Crazy Farm!</b> 🌾\n\n"
        "🎮 <b>أقوى لعبة Web3 زراعية وقتالية على شبكة TON!</b>\n\n"
        "🌟 <b>مميزات اللعبة:</b>\n"
        "• 🐝 <b>مزرعة النحل:</b> تعدين مجاني لنقاط FARM وتطوير مستواك.\n"
        "• 🐶 <b>سباق الجري RUN 3D:</b> تفادى العوائق واجمع عملات <b>CFC</b> ومكافآت الترتيب!\n"
        "• ⚔️ <b>حلبة قتال الحيوانات PVP:</b> معارك تكتيكية 3v3 و 5v5 و 7v7 وجوائز كبرى.\n"
        "• 💎 <b>إيردروب TON:</b> ربط المحفظة وحفظ حصتك من توزيع عملات CFC عند الإدراج.\n\n"
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
                    "switch_inline_query": "تعال العب معي في Crazy Farm واجمع عملات CFC للإيردروب القادم! 🌾"
                },
                {
                    "text": "❓ كيفية اللعب ونظام المكافآت",
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
    if USE_REQUESTS:
        print("✅ Network: Using 'requests' with automated cloud proxy support.")
    else:
        print("ℹ️ Network: Using standard urllib with proxy handler.")
    set_bot_menu_button()
    
    offset = 0
    error_count = 0
    while True:
        try:
            # Low polling timeout (5s) prevents PythonAnywhere proxy from dropping the tunnel with 503
            updates_res = api_request("getUpdates", {"offset": offset, "timeout": 5})
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
                                "🌾 طريقة اللعب ونظام المكافآت:\n"
                                "1. اجمع نقاط مزرعة النحل المجانية وطور مستواك.\n"
                                "2. العب سباق الجري RUN 3D بالكلب وتفادَ العوائق لجمع عملات CFC.\n"
                                "3. شارك في معارك الـ PVP واهزم الأعداء للحصول على جوائز إضافية.\n"
                                "4. اربط محفظة TON لحفظ وتوثيق رصيدك لاستلام الإيردروب عند الإطلاق!"
                            )
                            answer_callback(cb_id, how_text)
            else:
                error_count += 1
                # Calm backoff prevents triggering proxy rate limits on free cloud hosting
                time.sleep(4)

        except KeyboardInterrupt:
            print("\n🛑 Bot stopped by user.")
            break
        except Exception as e:
            print(f"Polling loop error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_bot_polling()
