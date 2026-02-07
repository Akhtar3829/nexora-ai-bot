import os
import threading
import asyncio
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from google import genai

# --- 1. CONFIGURATION (Railway Variables se link) ---
# Railway Dashboard mein ADMIN_ID aur GEMINI_API_KEY hona zaroori hai
ADMIN_ID = int(os.environ.get("ADMIN_ID", 7851228033))
GEMINI_KEY = os.environ.get("AIzaSyBq-1LCTleN7dGsk9R8IWBumH6DXtPtpw8")

# AI Client Setup
client = genai.Client(api_key=GEMINI_KEY)

# --- 2. RAILWAY SERVER (Health Check) ---
app_flask = Flask(__name__)
@app_flask.route('/')
def health():
    return "Nexora AI is Active and Secure!"

def run_flask():
    # Railway ke port par server chalana taaki build "Active" rahe
    port = int(os.environ.get("PORT", 8080))
    app_flask.run(host='0.0.0.0', port=port)

# --- 3. AI AGENT LOGIC ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Security: Sirf aap (Admin) hi use kar sakte hain
    if user.id != ADMIN_ID:
        print(f"Unauthorized access attempt by: {user.id}")
        return 

    user_text = update.message.text
    try:
        # Latest Gemini 2.0 Flash model ka istemal
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=f"System: You are Nexora AI, a secure autonomous teammate. Master: {user.id}. Respond helpfully.\nUser: {user_text}"
        )
        bot_reply = response.text
    except Exception as e:
        print(f"AI Error: {e}")
        bot_reply = "⚠️ AI Connection Error. Railway mein GEMINI_API_KEY check karein."

    await update.message.reply_text(f"🛡️ **NEXORA SECURE-CORE**\n\n{bot_reply}", parse_mode='Markdown')

# --- 4. EXECUTION ---
if __name__ == '__main__':
    # Railway Dashboard mein aapne BOT_TOKEN dala hai
    token = os.environ.get("BOT_TOKEN")
    
    if token:
        # Flask ko background mein start karein
        threading.Thread(target=run_flask, daemon=True).start()
        
        # Telegram Bot start karein
        app_bot = ApplicationBuilder().token(token).build()
        app_bot.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        
        print("Nexora Shield Active. Waiting for Admin...")
        app_bot.run_polling(drop_pending_updates=True) # Conflict se bachne ke liye
    else:
        print("ERROR: BOT_TOKEN Railway Variables mein nahi mila!")
    
