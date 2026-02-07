import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from google import genai

# --- CONFIGURATION ---
ADMIN_ID = int(os.environ.get("ADMIN_ID", 7851228033))
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyBq-1LCTleN7dGsk9R8IWBumH6DXtPtpw8")

# Nayi Library ka Client Setup
client = genai.Client(api_key=GEMINI_KEY)

# --- RAILWAY SURVIVAL SERVER ---
app_flask = Flask(__name__)
@app_flask.route('/')
def health():
    return "Nexora AI is Online!"

def run_flask():
    # Railway ke port par server chalana taaki build "Active" rahe
    port = int(os.environ.get("PORT", 8080))
    app_flask.run(host='0.0.0.0', port=port)

# --- AI AGENT LOGIC ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != ADMIN_ID:
        return 

    try:
        # Gemini 2.0 Flash Model (Fast & Smart)
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=update.message.text
        )
        await update.message.reply_text(f"🛡️ **NEXORA SECURE-CORE**\n\n{response.text}", parse_mode='Markdown')
    except Exception as e:
        print(f"AI Error: {e}")
        await update.message.reply_text("⚠️ AI Connection Error. API Key check karein.")

# --- MAIN EXECUTION ---
if __name__ == '__main__':
    token = os.environ.get("BOT_TOKEN")
    
    if token:
        # Flask ko background mein start karein
        threading.Thread(target=run_flask, daemon=True).start()
        
        # Bot setup with 'drop_pending_updates' to avoid Conflict crashes
        app_bot = ApplicationBuilder().token(token).build()
        app_bot.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        
        print("Nexora Shield Active...")
        app_bot.run_polling(drop_pending_updates=True)
    else:
        print("ERROR: BOT_TOKEN missing in Railway Variables!")
    
