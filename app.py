import subprocess
import sys

# === Dependency Management ===
def install_dependencies():
    try:
        # Upgrade pip
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        # Install python-telegram-bot v13.15 (compatible with your code)
        subprocess.check_call([sys.executable, "-m", "pip", "install", "python-telegram-bot==13.15"])
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
        sys.exit(1)

# Run dependency installation
install_dependencies()


import logging
import re
import time
import random
from datetime import datetime, timedelta
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters
from flask import Flask
from threading import Thread

# === Configuration ===
BOT_TOKEN = '8440214867:AAFSxAGBQyPgneX71G-VBQIkBVPiRru9z04'
CHANNEL_ID = '@zonehaxx'
ADMIN_TELEGRAM_ID = 6337558175
ALLOWED_FORWARD_USERNAME = "zoneehaxxd"

# === Bot Start Time for Ping ===
bot_start_time = time.time()

# === Logging Setup ===
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# === Flask Keep-Alive ===
app = Flask('')
@app.route('/')
def home():
    return "✅ Feedback Bot is running."

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    Thread(target=run).start()

# === In-Memory Trackers ===
spam_tracker = {}
captcha_sessions = {}
muted_users = {}
banned_users = {}
scheduled_promotions = {}  # <--- New global dictionary

# === Duration Parser ===
def parse_duration(duration_str):
    try:
        if duration_str.endswith("s"):
            return int(duration_str[:-1])
        elif duration_str.endswith("m"):
            return int(duration_str[:-1]) * 60
        elif duration_str.endswith("h"):
            return int(duration_str[:-1]) * 3600
        elif duration_str.endswith("d"):
            return int(duration_str[:-1]) * 86400
        return int(duration_str)
    except:
        return 0

# === Admin Commands ===
def mute(update, context):
    if update.effective_user.id != ADMIN_TELEGRAM_ID:
        return
    if len(context.args) < 2:
        update.message.reply_text("Usage: /mute <user_id_or_username> <duration>")
        return
    user_key = context.args[0]
    duration = parse_duration(context.args[1])
    muted_users[user_key] = time.time() + duration
    update.message.reply_text(f"🔇 User {user_key} has been muted for {duration} seconds.")

def unmute(update, context):
    if update.effective_user.id != ADMIN_TELEGRAM_ID:
        return
    user_key = context.args[0] if context.args else None
    if user_key in muted_users:
        del muted_users[user_key]
        update.message.reply_text(f"✅ User {user_key} has been unmuted.")
    else:
        update.message.reply_text("The specified user is not currently muted.")

def ban(update, context):
    if update.effective_user.id != ADMIN_TELEGRAM_ID:
        return
    if len(context.args) < 2:
        update.message.reply_text("Usage: /ban <user_id_or_username> <duration>")
        return
    user_key = context.args[0]
    duration = parse_duration(context.args[1])
    banned_users[user_key] = time.time() + duration
    update.message.reply_text(f"⛔ User {user_key} has been banned for {duration} seconds.")

def unban(update, context):
    if update.effective_user.id != ADMIN_TELEGRAM_ID:
        return
    user_key = context.args[0] if context.args else None
    if user_key in banned_users:
        del banned_users[user_key]
        update.message.reply_text(f"✅ User {user_key} has been unbanned.")
    else:
        update.message.reply_text("The specified user is not currently banned.")

def admin_commands(update, context):
    if update.effective_user.id != ADMIN_TELEGRAM_ID:
        context.bot.send_message(chat_id=update.effective_chat.id, text="🚫 You are not authorized to access this command.")
        return

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            "🛠 *Admin Command Panel*\n\n"
            "/ping — View bot status and latency\n"
            "/mute `<user>` `<duration>` — Temporarily mute a user\n"
            "/unmute `<user>` — Unmute a user\n"
            "/ban `<user>` `<duration>` — Temporarily ban a user\n"
            "/unban `<user>` — Unban a user\n"
            "/admin — Show this help message\n"
            "/promote `<interval>` — Auto-forward replied message repeatedly\n"
            "/stats — Shows the live bot statistics only\n"
            "/cancelpromote — Cancel replied promotion\n\n"
            "🕒 Duration examples: `10s`, `5m`, `1h`, `2d`\n"
            "You can use `@username` or Telegram ID.\n\n"
            "⚠️ Only visible to administrators."
        ),
        parse_mode='Markdown'
    )

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

# === /start Command ===
def start(update, context):
    user = update.effective_user
    user_id = user.id
    username = f"@{user.username}" if user.username else "@N/A"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    context.bot.send_message(
        chat_id=ADMIN_TELEGRAM_ID,
        text=f"📥 /start received from {username} (ID: {user_id})\n🕐 Timestamp: {timestamp}"
    )

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            "👋 Welcome to the ZONEEHAXX Feedback Bot!\n\n"
            "Please submit any *feedback*, *bug reports*, *suggestions*, or attach relevant *files/screenshots* here.\n"
            "📞 For assistance, contact [@zoneehaxxd](https://t.me/zoneehaxxd).\n\n"
            "✅ We appreciate your contribution to improving 𝗭𝗢𝗡𝗘𝗘𝗛𝗔𝗫𝗫 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗗𝗘𝗟𝗨𝗫𝗘!"
        ),
        parse_mode='Markdown'
    )

    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    captcha_sessions[user_id] = num1 + num2
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"🧠 Verification required:\n\n*What is {num1} + {num2}?*",
        parse_mode='Markdown'
    )

# === Feedback Handler ===
def forward_feedback(update, context):
    message = update.message
    if not message:
        return

    user = message.from_user
    user_id = user.id
    username = f"@{user.username}" if user.username else "@N/A"
    user_key = str(user_id) if user_id else username
    now = time.time()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if user_key in banned_users and now < banned_users[user_key]:
        context.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        return

    if user_key in muted_users and now < muted_users[user_key]:
        context.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        context.bot.send_message(chat_id=message.chat.id, text="⛔ You are currently muted. Please try again later.")
        return

    if user_id in captcha_sessions:
        try:
            if message.text and int(message.text.strip()) == captcha_sessions[user_id]:
                del captcha_sessions[user_id]
                context.bot.send_message(chat_id=message.chat.id, text="✅ Verification successful. You may now send feedback.")
                context.bot.send_message(chat_id=ADMIN_TELEGRAM_ID, text=f"✅ CAPTCHA passed by {username} (ID: {user_id})\n🕐 {timestamp}")
            else:
                context.bot.send_message(chat_id=message.chat.id, text="❌ Incorrect answer. Please use /start to try again.")
        except:
            context.bot.send_message(chat_id=message.chat.id, text="❌ Invalid input. Please enter a number.")
        return

    if message.forward_date or message.forward_from or message.forward_from_chat:
        if user.username != ALLOWED_FORWARD_USERNAME:
            context.bot.send_message(chat_id=message.chat.id, text="🚫 Only messages forwarded from @zoneehaxxd are permitted.")
            return

    if user_id in spam_tracker and now < spam_tracker[user_id]['until']:
        remaining = int(spam_tracker[user_id]['until'] - now)
        context.bot.send_message(chat_id=message.chat.id, text=f"⏳ You are temporarily muted due to suspected spam. Please wait {remaining} seconds.")
        return

    if message.text and is_spam(message.text):
        spam_count = spam_tracker.get(user_id, {}).get('count', 0) + 1
        mute_duration = min(60, spam_count * 5)
        spam_tracker[user_id] = {'count': spam_count, 'until': now + mute_duration}
        context.bot.send_message(chat_id=message.chat.id, text=f"🚫 Your message was flagged as spam. You have been muted for {mute_duration} seconds.")
        return

    try:
        context.bot.forward_message(chat_id=CHANNEL_ID, from_chat_id=message.chat.id, message_id=message.message_id)
        context.bot.forward_message(chat_id=ADMIN_TELEGRAM_ID, from_chat_id=message.chat.id, message_id=message.message_id)
        context.bot.send_message(chat_id=message.chat.id, text="✅ Your feedback has been submitted successfully. Thank you for your input!")
        context.bot.send_message(chat_id=ADMIN_TELEGRAM_ID, text=f"📝 Feedback received from {username} (ID: {user_id})\n🕐 {timestamp}")
        if user_id in spam_tracker:
            del spam_tracker[user_id]
    except Exception as e:
        logging.error(f"Error forwarding message: {e}")
        context.bot.send_message(chat_id=message.chat.id, text="⚠️ An error occurred while processing your message. Please try again.")

# === /ping Command ===
def ping(update, context):
    user_id = update.effective_user.id
    if user_id != ADMIN_TELEGRAM_ID:
        context.bot.send_message(chat_id=update.effective_chat.id, text="🚫 You are not authorized to access this command.")
        return
    start = time.time()
    sent = context.bot.send_message(chat_id=update.effective_chat.id, text="Pinging...")
    end = time.time()
    latency = int((end - start) * 1000)
    uptime_seconds = int(time.time() - bot_start_time)
    uptime_str = str(timedelta(seconds=uptime_seconds))
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    context.bot.edit_message_text(
        chat_id=sent.chat_id,
        message_id=sent.message_id,
        text=(
            "🏓 *Bot Status Report*\n"
            f"🕒 Server Time: `{now}`\n"
            f"⏳ Uptime: `{uptime_str}`\n"
            f"📡 Latency: `{latency} ms`"
        ),
        parse_mode='Markdown'
    )

def stats(update, context):
    if update.effective_user.id != ADMIN_TELEGRAM_ID:
        context.bot.send_message(chat_id=update.effective_chat.id, text="🚫 You are not authorized to access this command.")
        return

    uptime_seconds = int(time.time() - bot_start_time)
    uptime_str = str(timedelta(seconds=uptime_seconds))
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            "📊 *Bot Statistics*\n\n"
            f"🕒 Server Time: `{now}`\n"
            f"⏳ Uptime: `{uptime_str}`\n"
            f"🔇 Muted Users: `{len(muted_users)}`\n"
            f"⛔ Banned Users: `{len(banned_users)}`\n"
            f"📢 Active Promotions: `{len(scheduled_promotions)}`"
        ),
        parse_mode='Markdown'
    )

# === /promote Command ===
# === /promote Command ===
def promote(update, context):
    if update.effective_user.id != ADMIN_TELEGRAM_ID:
        update.message.reply_text("🚫 You are not authorized to use this command.")
        return

    if len(context.args) < 1:
        update.message.reply_text("Usage: /promote <interval> (e.g. 10m, 1h)")
        return

    interval_str = context.args[0]
    interval_seconds = parse_duration(interval_str)

    if interval_seconds <= 0:
        update.message.reply_text("⛔ Invalid interval.")
        return

    message = update.message.reply_to_message
    if not message:
        update.message.reply_text("📌 You must reply to the message you want to promote.")
        return

    promotion_id = f"{message.chat.id}:{message.message_id}"
    scheduled_promotions[promotion_id] = {
        "from_chat_id": message.chat.id,
        "message_id": message.message_id,
        "interval": interval_seconds,
        "next_send": time.time() + interval_seconds,
        "count": 0
    }

    update.message.reply_text(f"✅ Message scheduled for promotion every {interval_seconds} seconds.")

def cancel_promote(update, context):
    if update.effective_user.id != ADMIN_TELEGRAM_ID:
        update.message.reply_text("❌ You are not authorized to use this command.")
        return

    if not update.message.reply_to_message:
        update.message.reply_text("⚠️ Please reply to the message you want to cancel promotion for.")
        return

    replied = update.message.reply_to_message
    promotion_id = f"{replied.chat.id}:{replied.message_id}"

    if promotion_id in scheduled_promotions:
        del scheduled_promotions[promotion_id]
        update.message.reply_text("🛑 Promotion has been cancelled.")
    else:
        update.message.reply_text("⚠️ No promotion was found for this message.")

# === Promotion Loop ===
def promotion_loop(bot):
    while True:
        now = time.time()
        for key, data in list(scheduled_promotions.items()):
            if now >= data["next_send"]:
                try:
                    bot.forward_message(
                        chat_id=CHANNEL_ID,
                        from_chat_id=data["from_chat_id"],
                        message_id=data["message_id"]
                    )
                    data["next_send"] = now + data["interval"]
                    data["count"] += 1

                    # Send log to admin
                    bot.send_message(
                        chat_id=ADMIN_TELEGRAM_ID,
                        text=(
                            "📣 *Promotion Log*\n"
                            f"✅ Sent to: `{CHANNEL_ID}`\n"
                            f"🕒 Interval: `{data['interval']}s`\n"
                            f"🔁 Times Promoted: `{data['count']}`"
                        ),
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    logging.error(f"Error in promotion loop: {e}")
        time.sleep(10)

# === Main ===
def main():
    updater = Updater(token=BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("ping", ping))
    dispatcher.add_handler(CommandHandler("mute", mute))
    dispatcher.add_handler(CommandHandler("unmute", unmute))
    dispatcher.add_handler(CommandHandler("ban", ban))
    dispatcher.add_handler(CommandHandler("unban", unban))
    dispatcher.add_handler(CommandHandler("admin", admin_commands))
    dispatcher.add_handler(CommandHandler("promote", promote, pass_args=True))
    dispatcher.add_handler(CommandHandler("cancelpromote", cancel_promote))
    dispatcher.add_handler(CommandHandler("stats", stats))
    dispatcher.add_handler(MessageHandler(Filters.all, forward_feedback))
    keep_alive()
    Thread(target=promotion_loop, args=(updater.bot,), daemon=True).start()
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
