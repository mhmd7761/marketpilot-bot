import os
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai  # المكتبة الجديدة المطلوبة في السجلات

# إعداد Flask لإبقاء الخدمة نشطة على Render
app_flask = Flask('')
@app_flask.route('/')
def home(): return "Bot is Live!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app_flask.run(host='0.0.0.0', port=port)

# جلب المتغيرات من Render التي أضفتها
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

# إعداد مكتبة Gemini الجديدة
client = genai.Client(api_key=GEMINI_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 أهلاً بك! البوت يعمل الآن باستخدام الإصدار الجديد.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # استخدام المكتبة الجديدة لإرسال النص
        response = client.models.generate_content(model="gemini-1.5-flash", contents=update.message.text)
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text(f"⏳ حدث خطأ: {str(e)[:50]}")

if __name__ == '__main__':
    Thread(target=run_flask).start()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()
    
