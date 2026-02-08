import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler
from google import genai

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = os.environ.get("8296963784:AAFxdKKYnNf8Kc5VQQc-6LZeHPFZzRCKS0s", "")
GEMINI_API_KEY = os.environ.get("AIzaSyBq-1LCTleN7dGsk9R8IWBumH6DXtPtpw8", "")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "7851228033")

# Validate environment variables
if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN not found in environment!")
    raise ValueError("BOT_TOKEN is required")

if not GEMINI_API_KEY:
    logger.error("❌ GEMINI_API_KEY not found in environment!")
    raise ValueError("GEMINI_API_KEY is required")

logger.info("✅ Environment variables loaded successfully")

# Initialize Gemini AI Client
try:
    client = genai.Client(api_key=GEMINI_API_KEY)
    logger.info("✅ Gemini AI Client initialized")
except Exception as e:
    logger.error(f"❌ Failed to initialize Gemini AI Client: {e}")
    raise

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    user = update.effective_user
    welcome_message = f"""🎉 **NEXORA AI Bot is Active!**

नमस्ते {user.first_name}! 👋

मैं NEXORA AI हूँ - Google का Gemini 2.0 Flash मॉडल powered!

**मैं क्या कर सकता हूँ:**
✨ किसी भी सवाल का जवाब दूँ
💬 हिंदी और English में बात करूँ
🧠 Complex problems solve करूँ
📝 Content लिखूँ
🎨 Creative ideas दूँ

बस मुझे message भेजो और मैं तुरंत respond करूँगा!

**Commands:**
/start - Bot शुरू करें
/help - मदद लें
/about - मेरे बारे में जानें"""
    
    await update.message.reply_text(welcome_message, parse_mode='Markdown')
    logger.info(f"User {user.id} started the bot")

# Help command handler
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    help_text = """🆘 **NEXORA AI - Help Guide**

**कैसे use करें:**
1️⃣ मुझे कोई भी message भेजो
2️⃣ मैं तुरंत AI response दूँगा
3️⃣ हिंदी, English, या Hinglish - सब चलता है!

**Examples:**
• "भारत की राजधानी क्या है?"
• "Write a poem about technology"
• "Python में loop कैसे बनाते हैं?"
• "मुझे motivate करो"

**Tips:**
💡 Clear questions पूछो
💡 Context दो अगर ज़रूरत हो
💡 Creative बनो!

किसी problem के लिए admin से contact करो."""
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

# About command handler
async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send info about the bot."""
    about_text = """ℹ️ **About NEXORA AI**

🤖 **Model:** Google Gemini 2.0 Flash
⚡ **Speed:** Ultra-fast responses
🌐 **Languages:** Multiple languages supported
🔒 **Privacy:** Your chats are secure

**Powered by:**
• Google Gemini AI
• Python Telegram Bot
• Railway Hosting

**Developer:** @YourUsername

**Version:** 1.0.0
**Status:** 🟢 Active"""
    
    await update.message.reply_text(about_text, parse_mode='Markdown')

# Message handler with AI
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user messages and generate AI responses."""
    user = update.effective_user
    user_message = update.message.text
    
    logger.info(f"Message from {user.id}: {user_message[:50]}...")
    
    try:
        # Send typing action
        await update.message.chat.send_action(action="typing")
        
        # Generate AI response using Gemini
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=user_message
        )
        
        ai_reply = response.text
        
        # Send response
        await update.message.reply_text(ai_reply, parse_mode='Markdown')
        logger.info(f"Response sent to {user.id}")
        
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        error_message = f"⚠️ **AI Error**\n\nक्षमा करें, कुछ गड़बड़ी हुई:\n`{str(e)}`\n\nकृपया फिर से try करें या admin से संपर्क करें।"
        await update.message.reply_text(error_message, parse_mode='Markdown')

# Error handler
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors caused by updates."""
    logger.error(f"Update {update} caused error {context.error}")

# Main function
def main():
    """Start the bot."""
    logger.info("🚀 Starting NEXORA AI Bot...")
    
    # Create application
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about_command))
    
    # Add message handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Add error handler
    app.add_error_handler(error_handler)
    
    # Get bot info
    logger.info("✅ Bot handlers configured")
    
    # Start polling
    logger.info("✅ Bot is running and listening for messages...")
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Critical error: {e}")
        raise
