import os
import asyncio
import logging
from aiohttp import web
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')

logger.info(f"TOKEN: {TOKEN}")
logger.info(f"WEBHOOK_URL: {WEBHOOK_URL}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! لینک یوتیوب بفرست.")

async def webhook(request):
    logger.info("Webhook received!")
    try:
        app = request.app
        update = Update.de_json(await request.json(), app.bot)
        await app['dispatcher'].process_update(update)
    except Exception as e:
        logger.error(f"Error processing update: {e}")
    return web.Response()

async def main():
    logger.info("Starting bot...")
    
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    
    await app.initialize()
    await app.bot.set_webhook(WEBHOOK_URL)
    logger.info(f"Webhook set to: {WEBHOOK_URL}")
    
    server = web.Application()
    server['dispatcher'] = app
    server.router.add_post('/webhook', webhook)
    
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"Starting server on port {port}")
    
    runner = web.AppRunner(server)
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', port).start()
    
    logger.info("Server is running!")
    
    while True:
        await asyncio.sleep(3600)

if __name__ == '__main__':
    asyncio.run(main())
