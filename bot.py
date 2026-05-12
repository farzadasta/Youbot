import asyncio
import logging
from aiohttp import web
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "8690667258:AAEynP9DJpq-7Psl_sPt_QdJ-lLExl9ST1I"
WEBHOOK_URL = "https://youbot-64ua.onrender.com/webhook"

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

async def webhook(request):
    bot = request.app['bot']
    update = Update.de_json(await request.json(), bot)
    await request.app['application'].update_queue.put(update)
    return web.Response()

async def on_startup(app):
    app['application'] = ApplicationBuilder().token(TOKEN).build()
    app['bot'] = app['application'].bot
    
    app['application'].add_handler(CommandHandler("start", start))
    app['application'].add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))
    
    await app['bot'].set_webhook(WEBHOOK_URL)
    logger.info(f"Webhook set to: {WEBHOOK_URL}")

if __name__ == '__main__':
    app = web.Application()
    app['bot'] = None
    app['application'] = None
    
    app.router.add_post('/webhook', webhook)
    app.on_startup.append(on_startup)
    
    web.run_app(app, host='0.0.0.0', port=5000)
