import os
import logging
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from google import genai

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- SAHI TARIKA (Railway Variables Read Karna) ---
ADMIN_ID_RAW = os.environ.get("ADMIN_ID")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

# Convert ADMIN_ID to int safely
try:
    ADMIN_ID = int(ADMIN_ID_RAW) if ADMIN_ID_RAW else 7851228033
except ValueError:
    ADMIN_ID = 7851228033
    logger.warning("Invalid ADMIN_ID in Railway, using default.")

# Debug info (Sirf ye dikhayega ki data mila ya nahi)
logger.info(f"DEBUG: BOT_TOKEN Status: {'FOUND' if BOT_TOKEN else 'MISSING'}")
logger.info(f"DEBUG: GEMINI_KEY Status: {'FOUND' if GEMINI_KEY else 'MISSING'}")

# AI Client Setup
client = genai.Client(api_key=GEMINI_KEY) if GEMINI_KEY else None

# Railway Survival Server (Flask)
app = Flask(__name__)

@app.route('/')
def home():
    return "Nexora is Alive! ✅"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        if user_id != ADMIN_ID:
            await update.message.reply_text("❌ Access Denied.")
            return 
        
        if not client:
            await update.message.reply_text("⚠️ AI Service not configured.")
            return
            
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=update.message.text
        )
        await update.message.reply_text(f"🛡️ **NEXORA**\n\n{response.text}", parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == '__main__':
    # Start Flask in background
    threading.Thread(target=run_flask, daemon=True).start()
    
    # Start Telegram bot
    if BOT_TOKEN and GEMINI_KEY:
        try:
            bot_app = ApplicationBuilder().token(BOT_TOKEN).build()
            bot_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
            logger.info("🤖 Bot is starting...")
            bot_app.run_polling(drop_pending_updates=True)
        except Exception as e:
            logger.error(f"Bot error: {e}")
    else:
        logger.error("❌ Critical Variables Missing!")
    
