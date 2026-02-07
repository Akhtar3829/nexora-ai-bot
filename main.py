import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)
from google import genai

# ================= ENV VARIABLES =================
BOT_TOKEN = os.getenv("8296963784:AAFxdKKYnNf8Kc5VQQc-6LZeHPFZzRCKS0s")        # ✔️ Railway se
ADMIN_ID = int(os.getenv("ADMIN_ID", "7851228033"))  # ✔️ Railway se
GEMINI_API_KEY = os.getenv("AIzaSyDNQQ4VpxDgpoa9WMEb0DdVGfg3xWokAD0")

# ================= AI CLIENT =================
client = genai.Client(api_key=GEMINI_API_KEY)

# ================= FLASK =================
app = Flask(__name__)

@app.route("/")
def home():
    return "Nexora AI is running"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# ================= BOT =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *NEXORA AI ONLINE*\n\nMessage bhejo.",
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if user.id != ADMIN_ID:
        await update.message.reply_text("❌ Access denied")
        return

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=update.message.text
        )
        reply = response.text
    except Exception as e:
        reply = f"⚠️ AI Error: {e}"

    await update.message.reply_text(reply)

# ================= MAIN =================
if __name__ == "__main__":
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN missing in Railway variables")

    threading.Thread(target=run_flask, daemon=True).start()

    app_bot = ApplicationBuilder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🚀 Nexora AI Started")
    app_bot.run_polling()
