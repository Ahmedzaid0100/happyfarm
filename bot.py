"""
🌾 Happy Farm - Official Telegram Bot Backend
This bot handles:
1. /start command with a rich Welcome Message and Inline WebApp Launch Button.
2. Direct '🎮 Play Now' button opening the Happy Farm Mini App.
3. Referral system tracking (invited by friend).
4. Community & Support Links.
"""

import os
import sys
import json
import time
import urllib.request
import urllib.parse

# ==================== CONFIGURATION ====================
# Replace with your Bot Token from @BotFather, or set TELEGRAM_BOT_TOKEN environment variable
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
WEBAPP_URL = "https://ahmedzaid0100.github.io/happyfarm/"
CHANNEL_URL = "https://t.me/happyfarmHFC" # Replace with your channel if different

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def api_request(method, data=None):
    url = f"{API_URL}/{method}"
    headers = {"Content-Type": "application/json"}
    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        print(f"API Error [{method}]: {e}")
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
                    "text": "📢 القناة الرسمية",
                    "url": CHANNEL_URL
                },
                {
                    "text": "👥 دعوة الأصدقاء",
                    "switch_inline_query": "تعال العب معي في Crazy Farm واكسب عملات CFC مجاناً! 🌾"
                }
            ],
            [
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
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE" or not BOT_TOKEN:
        print("⚠️ Please set your BOT_TOKEN from @BotFather in bot.py or via environment variable!")
        return

    print("🚀 Starting Happy Farm Telegram Bot Polling...")
    set_bot_menu_button()
    
    offset = 0
    while True:
        try:
            updates_res = api_request("getUpdates", {"offset": offset, "timeout": 30})
            if updates_res and updates_res.get("ok"):
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
                            print(f"📥 /start from user: {first_name} (@{username}, ID: {user.get('id')})")
                            send_welcome_message(chat_id, first_name, username)

                    # Handle Callback Queries (like how_to_play)
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

        except KeyboardInterrupt:
            print("\n🛑 Bot stopped by user.")
            break
        except Exception as e:
            print(f"Polling loop error: {e}")
            time.sleep(3)

if __name__ == "__main__":
    run_bot_polling()
