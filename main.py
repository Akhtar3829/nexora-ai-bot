import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import google.generativeai as genai

# --- 1. CONFIGURATION ---
ADMIN_ID = 7851228033 
genai.configure(api_key="AIzaSyDNQQ4VpxDgpoa9WMEb0DdVGfg3xWokAD0")
model = genai.GenerativeModel('gemini-pro')

# --- 2. RAILWAY HEALTH SERVER (Zaroori hai) ---
app_flask = Flask(__name__)
@app_flask.route('/')
def health():
    return "Nexora is Running!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app_flask.run(host='0.0.0.0', port=port)

# --- 3. AI BOT LOGIC ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Security: Sirf aapke liye
    if user.id != ADMIN_ID:
        return 

    user_text = update.message.text
    
    try:
        # AI Agent Instruction
        prompt = f"System: You are Nexora AI, a secure autonomous teammate. Master: {user.id}. \nUser: {user_text}"
        response = model.generate_content(prompt)
        bot_reply = response.text
    except Exception as e:
        bot_reply = "⚠️ AI Error. API Key check karein."

    full_response = f"🛡️ **NEXORA SECURE-CORE**\n\n{bot_reply}"
    await update.message.reply_text(full_response, parse_mode='Markdown')

# --- 4. STARTING (Sirf Ek Baar) ---
if __name__ == '__main__':
    token = os.environ.get("TELEGRAM_TOKEN")
    
    if token:
        # Flask ko background mein chalana
        threading.Thread(target=run_flask, daemon=True).start()
        
        # Bot setup
        app_bot = ApplicationBuilder().token(token).build()
        app_bot.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        
        print("Nexora Shield Active...")
        app_bot.run_polling()
        
