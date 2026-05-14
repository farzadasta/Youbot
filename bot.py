import os
import time
import telebot
from pytube import YouTube

# دریافت توکن از متغیر محیطی (برای اجرا در هاست)
# اگر متغیر محیطی تعریف نشده بود، از توکن پیش‌فرض استفاده می‌کند (فقط برای تست محلی)
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '8690667258:AAEynP9DJpq-7Psl_sPt_QdJ-lLExl9ST1I')

# ساخت ربات
bot = telebot.TeleBot(TOKEN)

# پیام خوش‌آمدگویی
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(
        message,
        "سلام! 👋\n\n"
        "من یک ربات دانلودر از یوتیوب هستم.\n"
        "کافی است لینک یک ویدیو از یوتیوب را برای من بفرستید.\n"
        "من آن را با بهترین کیفیت ممکن دانلود کرده و برایتان ارسال می‌کنم.\n\n"
        "⚠️ توجه: حجم ویدیو نباید بیشتر از 50 مگابایت باشد (محدودیت تلگرام)."
    )

# مدیریت پیام‌های دریافتی (لینک یوتیوب)
@bot.message_handler(func=lambda m: True)
def download_video(message):
    url = message.text.strip()

    # بررسی معتبر بودن لینک یوتیوب
    if 'youtube.com' in url or 'youtu.be' in url:
        # پیام وضعیت دانلود
        status_msg = bot.reply_to(message, "📥 در حال دریافت اطلاعات ویدیو... لطفاً صبر کنید ⏳")

        # ساخت نام فایل یکتا (بر اساس chat_id و زمان جاری)
        filename = f"video_{message.chat.id}_{int(time.time())}.mp4"

        try:
            # دریافت ویدیو از یوتیوب
            yt = YouTube(url)
            # انتخاب بهترین کیفیت ممکن
            stream = yt.streams.get_highest_resolution()
            # دانلود فایل
            stream.download(output_path='.', filename=filename)

            # ویرایش پیام وضعیت
            bot.edit_message_text(
                "✅ دانلود کامل شد! در حال ارسال ویدیو...",
                chat_id=message.chat.id,
                message_id=status_msg.message_id
            )

            # ارسال ویدیو به کاربر
            with open(filename, 'rb') as video_file:
                bot.send_video(
                    message.chat.id,
                    video_file,
                    caption=f"🎬 {yt.title}\n\n👤 کانال: {yt.author}",
                    supports_streaming=True
                )

            # پاک کردن پیام وضعیت
            bot.delete_message(message.chat.id, status_msg.message_id)

        except Exception as e:
            # در صورت بروز خطا، به کاربر اطلاع بده
            bot.edit_message_text(
                f"❌ خطا در دانلود:\n{str(e)}",
                chat_id=message.chat.id,
                message_id=status_msg.message_id
            )
        finally:
            # حذف فایل ویدیو از روی دیسک (حتی اگر خطا رخ داده باشد)
            if os.path.exists(filename):
                os.remove(filename)
    else:
        # اگر لینک معتبر نبود
        bot.reply_to(message, "❌ لطفاً یک لینک معتبر از یوتیوب ارسال کنید.\n\nمثال:\nhttps://youtu.be/...\nhttps://www.youtube.com/watch?v=...")

# اجرای ربات
if __name__ == '__main__':
    print("🚀 ربات روشن شد...")
    bot.infinity_polling()
