import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler
from google import genai

# --- CONFIGURATION ---
ADMIN_ID = 7851228033
# Railway hamesha 'BOT_TOKEN' use karega
BOT_TOKEN = os.environ.get("8296963784:AAFxdKKYnNf8Kc5VQQc-6LZeHPFZzRCKS0s")

# API KEY FIX: Pehle Railway variable check karega, fir backup key
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyDNQQ4VpxDgpoa9WMEb0DdVGfg3xWokAD0")

# AI Client Setup
client = genai.Client(api_key=GEMINI_KEY)

# --- RAILWAY SURVIVAL SERVER ---
app = Flask(__name__)
@app.route('/')
def home():
    return "Nexora AI is Active!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- BOT LOGIC ---j
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return 

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=update.message.text
        )
        await update.message.reply_text(f"🛡️ **NEXORA**\n\n{response.text}", parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"⚠️ AI Error: {str(e)}")

if __name__ == '__main__':
    if BOT_TOKEN:
        threading.Thread(target=run_flask, daemon=True).start()
        bot_app = ApplicationBuilder().token(BOT_TOKEN).build()
        bot_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        
        print("Nexora Shield Active...")
        bot_app.run_polling(drop_pending_updates=True)
    else:
        print("CRITICAL: BOT_TOKEN not found!")
    
