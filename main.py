import os
import asyncio
import logging
import nest_asyncio
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai

# إعداد السجلات لمراقبة العمل من لوحة Render
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# حل مشكلة حلقة الأحداث (Event Loop) في السحابة
nest_asyncio.apply()

# --- 1. إعداد خادم ويب بسيط لإرضاء منصة Render ---
app_flask = Flask('')

@app_flask.route('/')
def home():
    return "MarketPilot AI is Live!"

def run_flask():
    # Render يمرر المنفذ عبر متغير PORT تلقائياً
    port = int(os.environ.get("PORT", 8080))
    app_flask.run(host='0.0.0.0', port=port)

# --- 2. إعداد ذكاء Gemini الاصطناعي ---
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_KEY)

# --- 3. دوام البوت (Handlers) ---

# ترحيب البوت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 أهلاً بك يا أبو علي في MarketPilot AI!\n"
        "أرسل لي اسم المنتج أو الخدمة وسأقوم بتصميم خطة تسويقية فوراً."
    )

# معالجة الرسائل وإرسالها لـ Gemini
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    try:
        # إرسال الطلب لنموذج جيميناي
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=user_input
        )
        await update.message.reply_text(response.text)
    except Exception as e:
        logging.error(f"⚠️ خطأ في Gemini: {e}")
        await update.message.reply_text("⏳ واجهت مشكلة في معالجة الطلب، تأكد من صلاحيات المفتاح.")

# --- 4. تشغيل التطبيق ---
if __name__ == '__main__':
    # تشغيل Flask في خيط منفصل (Background Thread)
    Thread(target=run_flask).start()
    
    # بناء تطبيق التلغرام
    TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()
    
    # إضافة الأوامر
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    # بدء الاستماع للرسائل (مع تجاهل الرسائل القديمة لتجنب التعارض)
    logging.info("البوت بدأ العمل الآن...")
    app.run_polling(drop_pending_updates=True)
    
