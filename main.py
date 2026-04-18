import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai

# إعداد السجلات لمراقبة الأخطاء في Render
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# جلب المفاتيح من إعدادات Render (Environment Variables)
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

# إعداد Gemini بالاصدار الجديد
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 أهلاً بك يا أبو علي! أرسل اسم منتجك وسأقوم بتصميم حملة تسويقية لك.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    try:
        # الاتصال بـ Gemini لتوليد المحتوى
        response = model.generate_content(user_text)
        await update.message.reply_text(response.text)
    except Exception as e:
        # طباعة الخطأ الحقيقي في سجلات Render لنعرف السبب بدقة
        logging.error(f"Error calling Gemini: {e}")
        await update.message.reply_text("⏳ حدث خطأ في الاتصال بالذكاء الاصطناعي، يرجى المحاولة لاحقاً.")

if __name__ == '__main__':
    # بناء التطبيق بالطريقة المتوافقة مع سجلاتك (V20+)
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    app.run_polling()
    
