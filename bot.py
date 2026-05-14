import os
import time
import telebot
import yt_dlp  # کتابخانه جدید را فراخوانی می‌کنیم

TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '8690667258:AAEynP9DJpq-7Psl_sPt_QdJ-lLExl9ST1I')
bot = telebot.TeleBot(TOKEN)
# حتماً این خط را داشته باشید تا Webhook قبلی پاک شود
bot.delete_webhook()

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "سلام! 👋\nلطفاً لینک ویدیوی یوتیوب را بفرستید.")

@bot.message_handler(func=lambda m: True)
def download_video(message):
    url = message.text.strip()

    if not ('youtube.com' in url or 'youtu.be' in url):
        bot.reply_to(message, "❌ لطفاً یک لینک معتبر از یوتیوب ارسال کنید.")
        return

    status_msg = bot.reply_to(message, "📥 در حال دانلود... لطفاً صبر کنید ⏳")
    filename = f"video_{message.chat.id}_{int(time.time())}.mp4"

    # تنظیمات yt-dlp برای دانلود بهترین کیفیت
    ydl_opts = {
        'outtmpl': filename,  # مسیر ذخیره فایل
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',  # کیفیت بهترین ویدیو و صدا
        'merge_output_format': 'mp4',  # در نهایت یک فایل mp4 داشته باشیم
        'quiet': True,  # خروجی اضافی چاپ نشود
        'no_warnings': True,  # هشدارها را نشان نده
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # اطلاعات ویدیو را می‌گیریم و همزمان دانلود می‌کند
            info = ydl.extract_info(url, download=True)
            video_title = info.get('title', 'ویدیو')

        # ویرایش پیام وضعیت
        bot.edit_message_text("✅ دانلود کامل شد! در حال ارسال ویدیو...",
                            chat_id=message.chat.id,
                            message_id=status_msg.message_id)

        # ارسال ویدیو به کاربر
        with open(filename, 'rb') as video_file:
            bot.send_video(message.chat.id,
                           video_file,
                           caption=f"🎬 {video_title}",
                           supports_streaming=True)

        # پاک کردن پیام وضعیت و حذف فایل
        bot.delete_message(message.chat.id, status_msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ خطا در دانلود:\n{str(e)}",
                            chat_id=message.chat.id,
                            message_id=status_msg.message_id)
    finally:
        if os.path.exists(filename):
            os.remove(filename)

if __name__ == '__main__':
    print("🚀 ربات با yt-dlp روشن شد...")
    bot.infinity_polling()
