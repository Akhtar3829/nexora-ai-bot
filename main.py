import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import google.generativeai as genai

# --- CONFIGURATION ---
# Apni Telegram ID yahan confirm karein
ADMIN_ID = 7851228033 

# Gemini API Key Setup
genai.configure(api_key="AIzaSyDNQQ4VpxDgpoa9WMEb0DdVGfg3xWokAD0")
model = genai.GenerativeModel('gemini-pro')

# --- RAILWAY FIX: HEALTH CHECK SERVER ---
server = Flask(__name__)
@server.route('/')
def health_check():
    return "Nexora AI is Online and Secure!"

def run_flask():
    # Railway ke port par server chalana
    port = int(os.environ.get("PORT", 5000))
    server.run(host='0.0.0.0', port=port)

# --- AI AGENT LOGIC ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Security: Sirf aapke orders sunega
    if user.id != ADMIN_ID:
        return 

    user_text = update.message.text
    
    try:
        # AI ko role dena (Autonomous Agent Mode)
        prompt = (
            f"System: You are NEXORA AI, a secure autonomous teammate. "
            f"You provide expert answers and help with tasks. "
            f"Master User ID: {user.id}. Reply in a natural, helpful way.\n"
            f"User: {user_text}"
        )
        response = model.generate_content(prompt)
        bot_reply = response.text
    except Exception as e:
        bot_reply = "⚠️ Connection Error: AI tak message nahi pahuch raha."

    # Final Response Header
    full_response = f"🛡️ **NEXORA SECURE-CORE**\n\n{bot_reply}"
    await update.message.reply_text(full_response, parse_mode='Markdown')

# --- MAIN EXECUTION ---
if __name__ == '__main__':
    token = os.environ.get("TELEGRAM_TOKEN")
    
    if not token:
        print("Error: TELEGRAM_TOKEN environment variable mein nahi mila!")
    else:
        # 1. Background mein Flask server start karein
        threading.Thread(target=run_flask, daemon=True).start()
        
        # 2. Telegram Bot start karein
        app = ApplicationBuilder().token(token).build()
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        
        print("Nexora Agent is Running. Security Active.")
        app.run_polling()
        
