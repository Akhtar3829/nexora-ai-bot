import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler
import google.generativeai as genai

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = os.environ.get("8296963784:AAFxdKKYnNf8Kc5VQQc-6LZeHPFZzRCKS0s", "")
GEMINI_API_KEY = os.environ.get("AIzaSyBq-1LCTleN7dGsk9R8IWBumH6DXtPtpw8", "")
ADMIN_ID = int(os.environ.get("7851228033", "0"))

# Validate environment variables
if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN not found!")
    raise ValueError("BOT_TOKEN is required")

if not GEMINI_API_KEY:
    logger.error("❌ GEMINI_API_KEY not found!")
    raise ValueError("GEMINI_API_KEY is required")

logger.info("✅ Environment variables loaded")

# Configure Gemini AI
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    logger.info("✅ Gemini AI configured successfully")
except Exception as e:
    logger.error(f"❌ Gemini configuration failed: {e}")
    raise

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome = f"""🎉 **NEXORA AI Active!**

नमस्ते {user.first_name}! 👋

मैं NEXORA AI हूँ - Google Gemini 2.0 Flash powered!

**Features:**
✨ Any question का जवाब
💬 हिंदी + English support
🧠 Problem solving
📝 Content writing
🎨 Creative ideas

बस message भेजो और जवाब पाओ!

**Commands:**
/start - शुरू करें
/help - मदद
/about - info"""
    
    await update.message.reply_text(welcome, parse_mode='Markdown')
    logger.info(f"User {user.id} started bot")

# Help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """🆘 **Help Guide**

**Use कैसे करें:**
1️⃣ कोई भी question पूछो
2️⃣ मैं AI response दूँगा
3️⃣ हिंदी/English दोनों OK!

**Examples:**
• "Python में loop कैसे बनाते हैं?"
• "भारत की राजधानी?"
• "Write a motivational quote"

**Tips:**
💡 Clear questions
💡 Context दो
💡 Creative बनो!"""
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

# About command
async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    about = """ℹ️ **NEXORA AI**

🤖 Model: Gemini 2.0 Flash
⚡ Speed: Ultra-fast
🌐 Multi-language
🔒 Secure

**Tech Stack:**
• Google Gemini AI
• Python Telegram Bot
• Railway Hosting

**Version:** 1.0
**Status:** 🟢 Active"""
    
    await update.message.reply_text(about, parse_mode='Markdown')

# Message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_message = update.message.text
    
    logger.info(f"Message from {user.id}: {user_message[:30]}...")
    
    try:
        # Typing action
        await update.message.chat.send_action(action="typing")
        
        # Generate AI response
        response = model.generate_content(user_message)
        ai_reply = response.text
        
        # Send response
        await update.message.reply_text(ai_reply)
        logger.info(f"Response sent to {user.id}")
        
    except Exception as e:
        logger.error(f"AI Error: {e}")
        error_msg = f"⚠️ Error: {str(e)[:100]}\n\nPlease try again!"
        await update.message.reply_text(error_msg)

# Error handler
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error: {context.error}")

# Main function
def main():
    logger.info("🚀 Starting NEXORA AI Bot...")
    
    # Build app
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)
    
    logger.info("✅ Handlers configured")
    logger.info("✅ Bot running! Waiting for messages...")
    
    # Start polling
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bot stopped")
    except Exception as e:
        logger.error(f"Critical error: {e}")
        raise
