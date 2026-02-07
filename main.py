import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from google import genai

# --- CONFIGURATION (Railway Variables se connect) ---
# Agar Railway mein ADMIN_ID hai toh wahan se lega, nahi toh niche wala number
ADMIN_ID = int(os.environ.get("ADMIN_ID", 7851228033))

# Gemini API Key Setup
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyDNQQ4VpxDgpoa9WMEb0DdVGfg3xWokAD0")
client = genai.Client(api_key=GEMINI_KEY)

# --- RAILWAY SERVER ---
app_flask = Flask(__name__)
@app_flask.route('/')
def health():
    return "Nexora is Active!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app_flask.run(host='0.0.0.0', port=port)

# --- AI BOT LOGIC ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Security: Railway ID ya Code ID se match karein
    if user.id != ADMIN_ID:
        print(f"Unauthorized access: {user.id}")
        return 

    user_text = update.message.text
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=f"System: You are Nexora AI, a secure autonomous teammate. Master: {user.id}. \nUser: {user_text}"
        )
        bot_reply = response.text
    except Exception as e:
        bot_reply = "⚠️ AI Connection Error. Railway variables check karein."

    await update.message.reply_text(f"🛡️ **NEXORA SECURE-CORE**\n\n{bot_reply}", parse_mode='Markdown')

# --- STARTING ---
if __name__ == '__main__':
    # Dashboard mein aapne BOT_TOKEN likha hai, toh wahi yahan use hoga
    token = os.environ.get("BOT_TOKEN")
    
    if token:
        threading.Thread(target=run_flask, daemon=True).start()
        app_bot = ApplicationBuilder().token(token).build()
        app_bot.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        print("Nexora Shield Active...")
        app_bot.run_polling()
    else:
        print("ERROR: BOT_TOKEN variable Railway mein nahi mila!")
        
