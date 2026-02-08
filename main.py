import os
import threading
import logging
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler
from google import genai

# --- 1. LOGGING SETUP (Taaki hume logs mein sab dikhe) ---
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- 2. CONFIGURATION (Railway Variables se automatic link) ---
# Hum code mein direct values nahi likhenge, Railway Variables use karenge
ADMIN_ID = int(os.environ.get("ADMIN_ID", 7851228033))
BOT_TOKEN = os.environ.get("8296963784:AAFxdKKYnNf8Kc5VQQc-6LZeHPFZzRCKS0s")
GEMINI_KEY = os.environ.get("AIzaSyDNQQ4VpxDgpoa9WMEb0DdVGfg3xWokAD0")

# AI Client Setup (Gemini 2.0 Flash)
client = genai.Client(api_key=GEMINI_KEY)

# --- 3. RAILWAY HEALTH SERVER (Crashes rokne ke liye) ---
app_flask = Flask(__name__)
@app_flask.route('/')
def health():
    return "🛡️ Nexora AI is Fully Operational!"

def run_flask():
    # Railway hamesha PORT variable deta hai, use hi use karna hai
    port = int(os.environ.get("PORT", 8080))
    app_flask.run(host='0.0.0.0', port=port)

# --- 4. BOT FUNCTIONS ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID:
        await update.message.reply_text("🛡️ **NEXORA SECURE-CORE ACTIVE**\n\nPranaam Master. Main aapka autonomous agent taiyaar hoon. Aap jo bhi puchenge, main uska turant jawab doonga.")
    else:
        await update.message.reply_text("❌ **Access Denied.** Sirf authorized admin hi mujhse sampark kar sakta hai.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Security: Sirf aapka ID allowed hai
    if user.id != ADMIN_ID:
        return 

    user_text = update.message.text
    
    try:
        # AI Se response lena (Gemini 2.0 Flash)
        # System Instruction AI ko batata hai ki use kaise behave karna hai
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=f"System: You are Nexora AI, a highly intelligent and secure autonomous agent. Your master's ID is {user.id}. Be brief, professional, and helpful.\nUser: {user_text}"
        )
        bot_reply = response.text
    except Exception as e:
        logging.error(f"AI Error: {e}")
        bot_reply = "⚠️ **AI Connection Error.** Railway Variables mein GEMINI_API_KEY check karein."

    # Response send karna
    await update.message.reply_text(f"🛡️ **NEXORA**\n\n{bot_reply}", parse_mode='Markdown')

# --- 5. MAIN EXECUTION ---
if __name__ == '__main__':
    if not BOT_TOKEN:
        print("CRITICAL ERROR: BOT_TOKEN variable Railway mein nahi mila!")
    else:
        # Flask ko background thread mein start karein
        threading.Thread(target=run_flask, daemon=True).start()
        
        # Telegram Bot Build karein
        app_bot = ApplicationBuilder().token(BOT_TOKEN).build()
        
        # Handlers lagana
        app_bot.add_handler(CommandHandler("start", start_command))
        app_bot.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        
        print("Nexora Agent is booting up...")
        
        # Conflict Fix: 'drop_pending_updates=True' se purane clash khatam ho jayenge
        app_bot.run_polling(drop_pending_updates=True)
