import os
import json
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

DATA_FILE = "memory.json"
SAFE_MODE = True

# ---------- Memory System ----------
def load_memory():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_memory(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

memory = load_memory()

# ---------- Language Detection ----------
def detect_language(text):
    hindi_chars = "अआइईउऊएऐओऔकखगघचछजझटठडढतथदधनपफबभमयरलवशषसह"
    for ch in text:
        if ch in hindi_chars:
            return "hi"
    return "en"

# ---------- AI Core (Phase-1 logic) ----------
def ai_response(user_id, text):
    lang = detect_language(text)

    blocked = ["hack", "cheat", "fraud", "scam"]
    if SAFE_MODE:
        for w in blocked:
            if w in text.lower():
                return "❌ Main illegal ya cheating ke kaam mein madad nahi karta."

    # save memory
    memory[str(user_id)] = memory.get(str(user_id), [])[-10:] + [text]
    save_memory(memory)

    if lang == "hi":
        return (
            "🤖 **NEXORA AI (Secure Mode)**\n\n"
            f"Aapne kaha:\n{text}\n\n"
            "Main aapki madad likhne, sochne aur kaam ko easy banane mein karta hoon."
        )
    else:
        return (
            "🤖 **NEXORA AI (Secure Mode)**\n\n"
            f"You said:\n{text}\n\n"
            "I help with writing, ideas, and productivity (safe & ethical)."
        )

# ---------- Telegram Handlers ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to **NEXORA AI**\n\n"
        "• Multi-language (Hindi / English)\n"
        "• Secure & Safe\n"
        "• Cloudbot-level assistant (mobile friendly)\n\n"
        "Bas message bhejo 🙂"
    )

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Aap admin nahi ho.")
        return

    await update.message.reply_text(
        "👑 **ADMIN PANEL**\n\n"
        "/safe_on – Safe mode ON\n"
        "/safe_off – Safe mode OFF\n"
        "/stats – User count\n"
        "/wipe_all – Memory clear"
    )

async def safe_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global SAFE_MODE
    if update.effective_user.id == ADMIN_ID:
        SAFE_MODE = True
        await update.message.reply_text("✅ Safe mode ENABLED")

async def safe_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global SAFE_MODE
    if update.effective_user.id == ADMIN_ID:
        SAFE_MODE = False
        await update.message.reply_text("⚠️ Safe mode DISABLED")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID:
        await update.message.reply_text(f"👥 Total users: {len(memory)}")

async def wipe_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID:
        memory.clear()
        save_memory(memory)
        await update.message.reply_text("🧹 All memory wiped")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply = ai_response(update.effective_user.id, update.message.text)
    await update.message.reply_text(reply)

# ---------- App Runner ----------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CommandHandler("safe_on", safe_on))
    app.add_handler(CommandHandler("safe_off", safe_off))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("wipe_all", wipe_all))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    app.run_polling()

if __name__ == "__main__":
    main()
