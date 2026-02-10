import os

# Ye lines debug karne ke liye hain
print("--- DEBUG START ---")
print(f"DEBUG: BOT_TOKEN is {'Set' if os.getenv('BOT_TOKEN') else 'NOT SET'}")
print(f"DEBUG: GEMINI_API_KEY is {'Set' if os.getenv('GEMINI_API_KEY') else 'NOT SET'}")
print(f"DEBUG: ADMIN_ID is {'Set' if os.getenv('ADMIN_ID') else 'NOT SET'}")
print("--- DEBUG END ---")

# Iske niche aapka baaki code shuru hoga...





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

# Railway dashboard se variables uthana - DEBUG MODE
logger.info("=== DEBUG: Loading environment variables ===")

ADMIN_ID = os.environ.get("7851228033")
BOT_TOKEN = os.environ.get("8296963784:AAFxdKKYnNf8Kc5VQQc-6LZeHPFZzRCKS0s")
GEMINI_KEY = os.environ.get("AIzaSyBq-1LCTleN7dGsk9R8IWBumH6DXtPtpw8")

# Debug print all variables (masked)
logger.info(f"ADMIN_ID exists: {bool(ADMIN_ID)}")
logger.info(f"BOT_TOKEN exists: {bool(BOT_TOKEN)}")
logger.info(f"GEMINI_API_KEY exists: {bool(GEMINI_KEY)}")

# Convert ADMIN_ID to int safely
try:
    ADMIN_ID = int(ADMIN_ID) if ADMIN_ID else 851228033
except ValueError:
    ADMIN_ID = 851228033
    logger.warning(f"Invalid ADMIN_ID, using default: {ADMIN_ID}")

# Check environment variables
if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN environment variable not set!")
else:
    logger.info("✅ BOT_TOKEN found")

if not GEMINI_KEY:
    logger.error("❌ GEMINI_API_KEY environment variable not set!")
else:
    logger.info("✅ GEMINI_API_KEY found")

# AI Client Setup
client = genai.Client(api_key=GEMINI_KEY) if GEMINI_KEY else None

# Railway Survival Server
app = Flask(__name__)

@app.route('/')
def home():
    return "Nexora is Alive! ✅"

@app.route('/debug')
def debug():
    return f"""
    <h1>Debug Info</h1>
    <p>BOT_TOKEN: {'SET' if BOT_TOKEN else 'NOT SET'}</p>
    <p>GEMINI_API_KEY: {'SET' if GEMINI_KEY else 'NOT SET'}</p>
    <p>ADMIN_ID: {ADMIN_ID}</p>
    """

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
        logger.info(f"📩 Received message from user {user_id}: {update.message.text[:50]}...")
        
        if user_id != ADMIN_ID:
            logger.warning(f"🚫 Unauthorized access attempt from user {user_id}")
            await update.message.reply_text("❌ Access Denied. Only admin can use this bot.")
            return 
        
        if not client:
            await update.message.reply_text("⚠️ AI Service not configured properly.")
            return
            
        user_message = update.message.text
        
        # Simple test first
        if user_message.lower() == "test":
            await update.message.reply_text("✅ Bot is working! AI service is ready.")
            return
            
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=user_message
        )
        
        await update.message.reply_text(
            f"🛡️ **NEXORA**\n\n{response.text}", 
            parse_mode='Markdown'
        )
        logger.info("✅ Response sent successfully")
        
    except Exception as e:
        logger.error(f"❌ Error in handle_message: {e}")
        await update.message.reply_text("⚠️ Error processing your request. Please try again.")

if __name__ == '__main__':
    import threading
    
    logger.info("=== STARTING APPLICATION ===")
    
    # Start Flask server in background
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Start Telegram bot if token exists
    if BOT_TOKEN and GEMINI_KEY:
        try:
            logger.info("🤖 Starting Telegram bot...")
            bot_app = ApplicationBuilder().token(BOT_TOKEN).build()
            bot_app.add_handler(
                MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
            )
            
            logger.info("✅ Bot application built successfully")
            bot_app.run_polling(
                drop_pending_updates=True,
                allowed_updates=Update.ALL_TYPES
            )
        except Exception as e:
            logger.error(f"❌ Bot startup error: {e}")
    else:
        logger.error("❌ Missing required environment variables! Running only Flask server.")
