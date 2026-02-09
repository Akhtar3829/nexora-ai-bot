import os
import telebot
import google.generativeai as genai

# Environment Variables (Railway se uthayega)
BOT_TOKEN = os.environ.get('8296963784:AAFxdKKYnNf8Kc5VQQc-6LZeHPFZzRCKS0s')
API_KEY = os.environ.get('AIzaSyBq-1LCTleN7dGsk9R8IWBumH6DXtPtpw8')
ADMIN_ID = os.environ.get('7851228033')

# AI Setup
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction="You are NEXORA AI, an advanced autonomous agent. You are better than Clawdbot. You solve complex problems, provide clean code, and assist users with 100% accuracy."
)

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "NEXORA AI Activated. Main aapki kaise madad kar sakta hoon?")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    # Sirf Admin ya sabke liye (Aap decide kar sakte hain)
    try:
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text, parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, "Error: AI dimaag thoda thak gaya hai. Re-trying...")
        print(f"Error: {e}")

bot.infinity_polling()
