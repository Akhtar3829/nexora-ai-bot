import os
import threading
import asyncio
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from google import genai

# --- CONFIGURATION ---
ADMIN_ID = 7851228033 
# Nayi library ke liye client setup
client = genai.Client(api_key="AIzaSyDNQQ4VpxDgpoa9WMEb0DdVGfg3xWokAD0")

# --- RAILWAY HEALTH SERVER ---
app_flask = Flask(__name__)
@app_flask.route('/')
def health():
    return "Nexora is Running!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app_flask.run(host='0.0.0.0', port=port)

# --- AI BOT LOGIC ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != ADMIN_ID:
        return 

    user_text = update.message.text
    try:
        # Naya AI response method
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=f"System: You are Nexora AI, a secure autonomous teammate. Master: {user.id}. \nUser: {user_text}"
        )
        bot_reply = response.text
    except Exception as e:
        bot_reply = "⚠️ AI Connection Error. API Key check karein."

    full_response = f"🛡️ **NEXORA SECURE-CORE**\n\n{bot_reply}"
    await update.message.reply_text(full_response, parse_mode='Markdown')

# --- STARTING ---
if __name__ == '__main__':
    token = os.environ.get("TELEGRAM_TOKEN")
    if token:
        threading.Thread(target=run_flask, daemon=True).start()
        app_bot = ApplicationBuilder().token(token).build()
        app_bot.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        print("Nexora Shield Active...")
        app_bot.run_polling()
    
