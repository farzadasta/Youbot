import os
import time
import asyncio
from pytube import YouTube
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')

if not TOKEN:
    raise ValueError("متغیر محیطی TELEGRAM_BOT_TOKEN تعریف نشده است")
if not WEBHOOK_URL:
    raise ValueError("متغیر محیطی WEBHOOK_URL تعریف نشده است")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! لینک ویدیوی یوتیوب را بفرستید تا برای شما دانلود کنم.")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not ('youtube.com' in url or 'youtu.be' in url):
        await update.message.reply_text("❌ لطفاً یک لینک معتبر یوتیوب بفرستید.")
        return

    status_msg = await update.message.reply_text("⏳ در حال دانلود... لطفاً صبر کنید.")
    filename = f"video_{update.effective_chat.id}_{int(time.time())}.mp4"

    try:
        yt = YouTube(url)
        stream = yt.streams.get_highest_resolution()
        if not stream:
            await update.message.reply_text("❌ ویدیویی یافت نشد.")
            return

        stream.download(output_path='.', filename=filename)
        with open(filename, 'rb') as f:
            await update.message.reply_video(f, caption=f"🎬 {yt.title}\n👤 {yt.author}")
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=status_msg.message_id)

    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {e}")
    finally:
        if os.path.exists(filename):
            os.remove(filename)

async def main():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    
    await application.initialize()
    await application.bot.set_webhook(WEBHOOK_URL)
    await application.start()
    
    print(f"✅ وب‌هوک فعال شد: {WEBHOOK_URL}")
    
    # نگه داشتن سرور
    while True:
        await asyncio.sleep(3600)

if __name__ == '__main__':
    asyncio.run(main())
