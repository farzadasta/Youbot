from flask import Flask, request
from telebot import TeleBot
import os
import yt_dlp

app = Flask(__name__)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set")

bot = TeleBot(TOKEN)

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_str = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
        return "OK", 200
    return "Bad Request", 400

@app.route("/")
def home():
    return "Bot is running!"

@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message, "سلام! لینک یوتیوب بفرست 🎥")

@bot.message_handler(func=lambda m: True)
def download(message):
    url = message.text.strip()
    if "youtube.com" not in url and "youtu.be" not in url:
        bot.reply_to(message, "لطفاً یک لینک معتبر یوتیوب بفرست.")
        return

    msg = bot.reply_to(message, "⏳ در حال دانلود...")

    try:
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'video.mp4',
            'quiet': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'video')

        with open('video.mp4', 'rb') as f:
            bot.send_video(message.chat.id, f, caption=title)

        os.remove('video.mp4')
        bot.delete_message(message.chat.id, msg.message_id)

    except Exception as e:
        bot.reply_to(message, f"❌ خطا: {str(e)}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
