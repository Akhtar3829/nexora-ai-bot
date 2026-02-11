import os
import threading
import logging
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from google import genai

# 1. Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 2. Railway dashboard se variables uthana
# Default ID 7851228033 rakhi hai jaisa aapne pehle bataya tha
ADMIN_ID = int(os.environ.get("ADMIN_ID", 7851228033))
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

# 3. AI Client Setup
client = genai.Client(api_key=GEMINI_KEY) if GEMINI_KEY else None

# 4. Railway Survival Server (Flask)
app = Flask(__name__)

@app.route('/')
def home():
    return "Nexora is Alive! ✅"

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

# 5. Message Handler (Main Logic)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        user_message = update.message.text
        
        # Admin ID check
        if user_id != ADMIN_ID:
            logger.warning(f"Unauthorized access: {user_id}")
            await update.message.reply_text("❌ Access Denied. Only admin can use this bot.")
            return 
        
        if not client:
            await update.message.reply_text("⚠️ AI Service not configured. Check API Key.")
            return

        # AI Response logic - Using stable gemini-1.5-flash
        response = client.models.generate_content(
            model="models/gemini-1.5-flash" 
            contents=user_message
        )
        
        # Markdown formatting ke saath reply
        await update.message.reply_text(
            f"🛡️ **NEXORA**\n\n{response.text}", 
            parse_mode='Markdown'
        )
        logger.info(f"✅ Response sent to {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Gemini Error: {e}")
        # Asli error bot par dikhane ke liye taaki debugging aasaan ho
        await update.message.reply_text(f"⚠️ AI Error: {str(e)}")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")

# 6. Main Execution
if __name__ == '__main__':
    if BOT_TOKEN and GEMINI_KEY:
        # Flask server background mein start karein
        threading.Thread(target=run_flask, daemon=True).start()
        
        try:
            # Telegram bot setup
            bot_app = ApplicationBuilder().token(BOT_TOKEN).build()
            bot_app.add_error_handler(error_handler)
            bot_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
            
            logger.info("🤖 NEXORA AI is starting...")
            bot_app.run_polling(drop_pending_updates=True)
            
        except Exception as e:
            logger.error(f"Fatal error: {e}")
    else:
        logger.error("❌ Missing BOT_TOKEN or GEMINI_API_KEY in Railway Variables!")
