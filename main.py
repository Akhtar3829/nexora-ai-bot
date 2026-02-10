import os
import threading
import logging
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from google import genai

# Setup logging for debugging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Railway dashboard se variables uthana
ADMIN_ID = int(os.environ.get("ADMIN_ID", 851228033))
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

# Check environment variables
if not BOT_TOKEN:
    logger.error("BOT_TOKEN environment variable not set!")
if not GEMINI_KEY:
    logger.error("GEMINI_API_KEY environment variable not set!")

# AI Client Setup
client = genai.Client(api_key=GEMINI_KEY) if GEMINI_KEY else None

# Railway Survival Server
app = Flask(__name__)

@app.route('/')
def home():
    return "Nexora is Alive!"

@app.route('/health')
def health():
    return "OK", 200

def run_flask():
    try:
        port = int(os.environ.get("PORT", 8080))
        logger.info(f"Starting Flask server on port {port}")
        app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
    except Exception as e:
        logger.error(f"Flask server error: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        logger.info(f"Received message from user {user_id}")
        
        if user_id != ADMIN_ID:
            logger.warning(f"Unauthorized access attempt from user {user_id}")
            await update.message.reply_text("❌ Access Denied.")
            return 
        
        if not client:
            await update.message.reply_text("⚠️ AI Service not configured.")
            return
            
        user_message = update.message.text
        logger.info(f"Processing message: {user_message[:50]}...")
        
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=user_message
        )
        
        await update.message.reply_text(
            f"🛡️ **NEXORA**\n\n{response.text}", 
            parse_mode='Markdown'
        )
        logger.info("Response sent successfully")
        
    except Exception as e:
        logger.error(f"Error in handle_message: {e}")
        await update.message.reply_text("⚠️ Error processing your request.")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")

if __name__ == '__main__':
    try:
        if BOT_TOKEN and GEMINI_KEY:
            # Flask server in separate thread
            flask_thread = threading.Thread(target=run_flask, daemon=True)
            flask_thread.start()
            logger.info("Flask server started in background")
            
            # Telegram bot setup
            bot_app = ApplicationBuilder() \
                .token(BOT_TOKEN) \
                .build()
            
            bot_app.add_error_handler(error_handler)
            bot_app.add_handler(
                MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
            )
            
            logger.info("Starting Telegram bot...")
            
            # Start polling with better parameters
            bot_app.run_polling(
                drop_pending_updates=True,
                allowed_updates=Update.ALL_TYPES,
                close_loop=False
            )
            
        else:
            logger.error("Missing required environment variables!")
            # Start only Flask if bot token missing
            run_flask()
            
    except Exception as e:
        logger.error(f"Fatal error: {e}")
