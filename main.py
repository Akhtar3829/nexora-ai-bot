import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get environment variables
BOT_TOKEN = os.getenv("8296963784:AAFxdKKYnNf8Kc5VQQc-6LZeHPFZzRCKS0s
")
GEMINI_API_KEY = os.getenv("AIzaSyBq-1LCTleN7dGsk9R8IWBumH6DXtPtpw8")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found in environment variables!")

logger.info("Bot token found, initializing...")

# Initialize Gemini AI (with error handling)
genai_model = None
try:
    import google.generativeai as genai
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        genai_model = genai.GenerativeModel('gemini-2.0-flash-exp')
        logger.info("✅ Gemini AI initialized successfully")
    else:
        logger.warning("⚠️ GEMINI_API_KEY not found, AI features disabled")
except Exception as e:
    logger.error(f"⚠️ Gemini initialization failed: {e}")
    logger.info("Bot will run without AI features")

# Command handlers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    user = update.effective_user
    message = f"""🎉 NEXORA AI Bot Active!

नमस्ते {user.first_name}! 👋

I'm powered by Google Gemini 2.0 Flash!

Commands:
/start - Start the bot
/help - Get help
/status - Check bot status

Just send me any message and I'll respond!"""
    
    await update.message.reply_text(message)
    logger.info(f"User {user.id} ({user.username}) started the bot")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command handler"""
    help_text = """🆘 HELP GUIDE

How to use:
1️⃣ Send me any question
2️⃣ I'll give you an AI response
3️⃣ Works in Hindi & English!

Examples:
• "What is Python?"
• "भारत की राजधानी क्या है?"
• "Write a poem about AI"

Commands:
/start - Start bot
/help - This message
/status - Check if AI is working"""
    
    await update.message.reply_text(help_text)

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Status command handler"""
    if genai_model:
        status = "✅ AI Status: ACTIVE\n🤖 Model: Gemini 2.0 Flash\n⚡ Ready to respond!"
    else:
        status = "⚠️ AI Status: DISABLED\n❌ Gemini API not configured\nPlease check GEMINI_API_KEY"
    
    await update.message.reply_text(status)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all text messages"""
    user = update.effective_user
    user_message = update.message.text
    
    logger.info(f"Message from {user.id}: {user_message[:50]}")
    
    # Check if AI is available
    if not genai_model:
        await update.message.reply_text(
            "⚠️ AI currently unavailable.\n"
            "Please contact admin to configure GEMINI_API_KEY."
        )
        return
    
    try:
        # Show typing indicator
        await update.message.chat.send_action(action="typing")
        
        # Generate AI response
        response = genai_model.generate_content(user_message)
        
        # Check if response has text
        if response.text:
            ai_reply = response.text
        else:
            ai_reply = "Sorry, I couldn't generate a response. Please try again."
        
        # Send response (split if too long)
        if len(ai_reply) > 4000:
            # Split into chunks
            for i in range(0, len(ai_reply), 4000):
                await update.message.reply_text(ai_reply[i:i+4000])
        else:
            await update.message.reply_text(ai_reply)
        
        logger.info(f"Response sent to {user.id}")
        
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        error_msg = (
            f"⚠️ Error occurred:\n{str(e)[:200]}\n\n"
            "Please try again or use /status to check bot health."
        )
        await update.message.reply_text(error_msg)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Log errors"""
    logger.error(f"Exception while handling an update: {context.error}")

def main():
    """Main function to run the bot"""
    logger.info("🚀 Starting NEXORA AI Bot...")
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    
    # Add message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    logger.info("✅ All handlers registered")
    logger.info("✅ Bot is now running and polling for updates...")
    
    # Start the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == '__main__':
    main()
