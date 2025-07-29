import logging
import re
import time
import random
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from flask import Flask
from threading import Thread

# === Hardcoded Bot Token and Channel ID ===
BOT_TOKEN = '8440214867:AAFSxAGBQyPgneX71G-VBQIkBVPiRru9z04'
CHANNEL_ID = '@zonehaxx'

# === Logging Setup ===
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# === Flask Keep-Alive ===
app = Flask('')

@app.route('/')
def home():
    return "✅ Feedback Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    Thread(target=run).start()

# === In-Memory Trackers ===
spam_tracker = {}
captcha_sessions = {}

# === Spam Filter ===
def is_spam(text):
    allowed_mentions = ["@zoneehaxxd"]
    spam_patterns = [
        r"http[s]?://",
        r"t\.me/",
        r"joinchat",
        r"(discord\.gg|bit\.ly|tinyurl\.com)",
        r"free\s*(cheat|hack|tool)",
        r"@[\w\d_]+"
    ]

    found_mentions = re.findall(r"@[\w\d_]+", text)
    for mention in found_mentions:
        if mention.lower() not in allowed_mentions:
            return True

    for pattern in spam_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True

    return False

# === /start Command with Welcome + CAPTCHA ===
def start(update, context):
    user_id = update.effective_user.id

    # Send welcome message first
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            "👋 *Welcome to ZONEEHAXX Feedback Bot!*\n\n"
            "🛠️ This bot is here to collect your *feedback*, *bug reports*, *suggestions*, and *files/screenshots* to help improve our tools and services.\n\n"
            "📤 Simply type your message or attach a file and send it here. We'll make sure it reaches our development team.\n\n"
            "📞 For direct assistance, you may contact us at [@zoneehaxxd](https://t.me/zoneehaxxd).\n\n"
            "✅ Thank you for being part of the ZONEEHAXX community!"
        ),
        parse_mode='Markdown'
    )

    # Generate math CAPTCHA
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    answer = num1 + num2
    captcha_sessions[user_id] = answer

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"🤖 Please solve this CAPTCHA to continue:\n\n*What is {num1} + {num2}?*",
        parse_mode='Markdown'
    )

# === Feedback Handler with CAPTCHA + Spam Check ===
def forward_feedback(update, context):
    message = update.message
    if not message:
        return

    user_id = message.from_user.id
    now = time.time()

    # CAPTCHA gate
    if user_id in captcha_sessions:
        try:
            if message.text and int(message.text.strip()) == captcha_sessions[user_id]:
                del captcha_sessions[user_id]
                context.bot.send_message(chat_id=message.chat.id, text="✅ CAPTCHA passed! You can now send feedback.")
            else:
                context.bot.send_message(chat_id=message.chat.id, text="❌ Wrong CAPTCHA. Please try again using /start.")
        except:
            context.bot.send_message(chat_id=message.chat.id, text="❌ Invalid answer. Please enter a number.")
        return

    # Block forwarded content
    if message.forward_date or message.forward_from or message.forward_from_chat:
        context.bot.send_message(
            chat_id=message.chat.id,
            text="🚫 Forwarded messages are not allowed. Please send your original feedback."
        )
        return

    # Check mute
    if user_id in spam_tracker and now < spam_tracker[user_id]['until']:
        remaining = int(spam_tracker[user_id]['until'] - now)
        context.bot.send_message(
            chat_id=message.chat.id,
            text=f"⏳ You're temporarily muted for spamming. Please wait {remaining} seconds before sending again."
        )
        return

    # Spam check
    if message.text and is_spam(message.text):
        spam_count = spam_tracker.get(user_id, {}).get('count', 0) + 1
        mute_duration = min(60, spam_count * 5)

        spam_tracker[user_id] = {
            'count': spam_count,
            'until': now + mute_duration
        }

        context.bot.send_message(
            chat_id=message.chat.id,
            text=f"🚫 Your message was flagged as spam.\nYou've been muted for {mute_duration} seconds. Avoid links, invites, or unknown mentions."
        )
        return

    # Forward valid message
    try:
        if message.photo or message.video or message.document:
            context.bot.forward_message(chat_id=CHANNEL_ID, from_chat_id=message.chat.id, message_id=message.message_id)
        elif message.text:
            context.bot.send_message(chat_id=CHANNEL_ID, text=message.text)
        else:
            context.bot.send_message(chat_id=CHANNEL_ID, text="📩 Received a feedback message.")

        context.bot.send_message(
            chat_id=message.chat.id,
            text="✅ Your feedback has been successfully submitted!\n\n🙏 Thank you for helping improve ZONEEHAXX PREMIUM DELUXE."
        )

        if user_id in spam_tracker:
            del spam_tracker[user_id]

    except Exception as e:
        print(f"Error while forwarding message: {e}")
        context.bot.send_message(chat_id=message.chat.id, text="⚠️ Something went wrong while forwarding your feedback.")

# === Main Function ===
def main():
    keep_alive()
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.all & ~Filters.command, forward_feedback))

    print("✅ Feedback bot is running...")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()