import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import google.generativeai as genai

# --- CONFIGURATION ---
# 1. Apni Telegram ID yahan likhein (userinfobot se jo mili)
ADMIN_ID = 7851228033

# 2. Gemini API Key configuration
genai.configure(api_key="AIzaSyDNQQ4VpxDgpoa9WMEb0DdVGfg3xWokAD0")
model = genai.GenerativeModel('gemini-pro')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # SECURITY SHIELD: Sirf Admin ko access dena
    if user.id != ADMIN_ID:
        print(f"Security Alert: Unauthorized user {user.id} tried to message.")
        return # Anjaan user ko koi reply nahi jayega

    user_text = update.message.text
    
    try:
        # AI Logic
        prompt = f"System: You are Nexora AI, a highly secure autonomous agent. User {user.id} is your master. Respond intelligently. \nUser: {user_text}"
        response = model.generate_content(prompt)
        bot_reply = response.text
    except Exception as e:
        bot_reply = "⚠️ Connection Error: Please check API Key or Internet."

    # Final Response
    full_response = f"🛡️ **NEXORA SECURE-CORE**\n\n{bot_reply}"
    await update.message.reply_text(full_response, parse_mode='Markdown')

if __name__ == '__main__':
    # Railway variables se token uthana
    token = os.environ.get("TELEGRAM_TOKEN")
    
    if not token:
        print("Error: TELEGRAM_TOKEN not found in environment variables.")
    else:
        app = ApplicationBuilder().token(token).build()
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        
        print("Nexora Shield Active. Only Admin can access.")
        app.run_polling()
            
