import os
import asyncio
import nest_asyncio
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai

# حل مشكلة حلقة الأحداث في البيئات السحابية
nest_asyncio.apply()

# إعداد Flask لفتح المنفذ المطلوب من Render
app_flask = Flask('')
@app_flask.route('/')
def home(): return "Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app_flask.run(host='0.0.0.0', port=port)

# جلب المفاتيح من المتغيرات التي أضفتها
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

# إعداد عميل Gemini الجديد
client = genai.Client(api_key=GEMINI_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 أهلاً بك! البوت متصل الآن بنجاح.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=update.message.text
        )
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text("⏳ عذراً، واجهت مشكلة بسيطة في الاتصال بـ Gemini.")

if __name__ == '__main__':
    # بدء خادم الويب في خلفية منفصلة
    Thread(target=run_flask).start()
    
    # بناء وتشغيل البوت
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Starting bot...")
    app.run_polling(drop_pending_updates=True)
    
