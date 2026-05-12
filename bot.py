import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# توکن مستقیم
TOKEN = "8690667258:AAEynP9DJpq-7Psl_sPt_QdJ-lLExl9ST1I"
WEBHOOK_URL = "https://youbot-64ua.onrender.com/webhook"

logger.info(f"TOKEN: {TOKEN}")
logger.info(f"WEBHOOK_URL: {WEBHOOK_URL}")

bot_app = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! لینک یوتیوب بفرست.")

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if 'youtube' not in url:
        await update.message.reply_text("لینک یوتیوب بفرست!")
        return
    
    msg = await update.message.reply_text("⏳ دانلود...")
    
    try:
        from pytube import YouTube
        yt = YouTube(url)
        video = yt.streams.get_highest_resolution()
        video.download(filename='video.mp4')
        
        with open('video.mp4', 'rb') as f:
            await update.message.reply_video(f, caption=yt.title)
        
        os.remove('video.mp4')
        await msg.delete()
    except Exception as e:
        await update.message.reply_text(f"خطا: {e}")

@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot_app.bot)
    bot_app.update_queue.put(update)
    return 'ok'

if __name__ == '__main__':
    logger.info("Building bot...")
    bot_app = ApplicationBuilder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))
    
    logger.info("Setting webhook...")
    bot_app.run_webhook(
        listen='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        url_path='',
        webhook_url=WEBHOOK_URL
    )
    
    logger.info("Starting Flask...")
    app.run(host='0.0.0.0', port=5000)
