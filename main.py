import os
import threading
import logging
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from google import genai

# -------------------- LOGGING SETUP --------------------
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# -------------------- ENV VARIABLES --------------------
ADMIN_ID = int(os.environ.get("ADMIN_ID", 7851228033))
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

# -------------------- GEMINI CLIENT --------------------
client = None
if GEMINI_KEY:
    client = genai.Client(api_key=GEMINI_KEY)

# -------------------- FLASK SERVER --------------------
app = Flask(__name__)

@app.route('/')
def home():
    return "Nexora is Alive! ✅"

@app.route('/health')
def health():
    return "OK", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"🌐 Flask running on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# -------------------- TELEGRAM HANDLER --------------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        user_message = update.message.text

        # Admin check
        if user_id != ADMIN_ID:
            await update.message.reply_text("❌ Access Denied.")
            return

        if not client:
            await update.message.reply_text("⚠️ AI not configured.")
            return

        # Gemini call
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=user_message
        )

        if response and response.text:
            await update.message.reply_text(
                f"🛡️ NEXORA AI\n\n{response.text}"
            )
        else:
            await update.message.reply_text("⚠️ Empty AI response.")

    except Exception as e:
        logger.error(f"Gemini Error: {e}")
        await update.message.reply_text("⚠️ AI service temporary unavailable.")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")

# -------------------- MAIN --------------------
if __name__ == '__main__':
    if BOT_TOKEN and GEMINI_KEY:

        # Start Flask in background
        threading.Thread(target=run_flask, daemon=True).start()

        try:
            bot_app = ApplicationBuilder().token(BOT_TOKEN).build()
            bot_app.add_handler(
                MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
            )
            bot_app.add_error_handler(error_handler)

            logger.info("🤖 NEXORA AI Started Successfully")
            bot_app.run_polling(drop_pending_updates=True)

        except Exception as e:
            logger.error(f"Fatal error: {e}")
    else:
        logger.error("❌ Missing BOT_TOKEN or GEMINI_API_KEY")
