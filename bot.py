import os
import time
from pytube import YouTube
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# خواندن توکن و آدرس وب‌هوک از متغیرهای محیطی
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
WEBHOOK_URL = os.environ.get('74.220.50.0/24
74.220.58.0/24')  # مثال: https://mybot.onrender.com

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

if __name__ == '__main__':
    # ساخت اپلیکیشن بدون polling
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    # تنظیم وب‌هوک روی آدرس رندر
    port = int(os.environ.get('PORT', 8080))  # Render پورت 8080 را فراهم می‌کند
    print(f"✅ شروع وب‌هوک روی پورت {port} با آدرس {WEBHOOK_URL}")
    application.run_webhook(
        listen='0.0.0.0',
        port=port,
        url_path=TOKEN,  # مسیر وب‌هوک (اختیاری، برای امنیت بیشتر)
        webhook_url=f"{WEBHOOK_URL}/{TOKEN}"
    )
