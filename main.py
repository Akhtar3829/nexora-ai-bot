import os
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# -------- CONFIG --------
BOT_TOKEN = os.getenv("8296963784:AAFxdKKYnNf8Kc5VQQc-6LZeHPFZzRCKS0s")
ADMIN_ID = int(os.getenv("ADMIN_ID", "7851228033"))
GEMINI_API_KEY = os.getenv("AIzaSyBq-1LCTleN7dGsk9R8IWBumH6DXtPtpw8")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN missing")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY missing")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# -------- BOT LOGIC --------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text

    if user.id != ADMIN_ID:
        return

    try:
        response = model.generate_content(text)
        reply = response.text
    except Exception as e:
        reply = f"⚠️ AI Error:\n{e}"

    await update.message.reply_text(reply)

# -------- START --------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 NEXORA AI running")
    app.run_polling()

if __name__ == "__main__":
    main()
