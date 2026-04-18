import os
import logging
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai

# 1. إعداد خادم Flask وهمي لإبقاء الخدمة تعمل على Render
app_flask = Flask('')

@app_flask.route('/')
def home():
    return "I am alive!"

def run_flask():
    # Render يتوقع استماع على منفذ، نستخدم 8080 بشكل افتراضي
    app_flask.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

# 2. إعداد السجلات (Logs)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# 3. جلب المفاتيح من إعدادات البيئة في Render
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

# 4. إعداد ذكاء Gemini الاصطناعي
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# دالة الترحيب /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 أهلاً بك يا أبو علي! أرسل اسم منتجك وسأقوم بتصميم حملة تسويقية لك.")

# دالة التعامل مع الرسائل النصية
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    try:
        # إرسال النص إلى Gemini وجلب الرد
        response = model.generate_content(user_text)
        await update.message.reply_text(response.text)
    except Exception as e:
        logging.error(f"Error calling Gemini: {e}")
        await update.message.reply_text("⏳ حدث ضغط بسيط، حاول مرة أخرى.")

if __name__ == '__main__':
    # تشغيل الخادم الوهمي في الخلفية
    keep_alive()
    
    # بناء تطبيق التلغرام (متوافق مع V20+ كما في سجلاتك)
    #
    app = ApplicationBuilder().token(TOKEN).build()
    
    # إضافة الأوامر والمستقبلات
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("البوت يعمل الآن ومستعد لاستقبال الرسائل...")
    app.run_polling()
    
