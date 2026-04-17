import os
import asyncio
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import openai

# --- 1. إعداد سيرفر وهمي لإرضاء منصة Render (Health Check) ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Bot is Live and Running!")

def run_health_check_server():
    # Render يرسل المنفذ تلقائياً عبر متغير بيئة يسمى PORT
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    print(f"Starting health check server on port {port}")
    server.serve_forever()

# --- 2. إعدادات المفاتيح (Environment Variables) ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# إعداد عميل OpenAI بالإصدار الحديث
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# --- 3. وظائف البوت ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 أهلاً بك في Market Pilot! أرسل لي اسم منتجك وسأقوم بإنشاء حملة تسويقية احترافية لك باستخدام الذكاء الاصطناعي.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    
    # رسالة انتظار للمستخدم
    waiting_msg = await update.message.reply_text("⏳ جاري تحليل المنتج وتوليد الحملة...")

    prompt = f"""
    أنت خبير تسويق رقمي. أنشئ حملة تسويقية متكاملة للمنتج التالي:
    المنتج: {user_input}
    
    المطلوب:
    1. إعلان جذاب لمنصات التواصل.
    2. 3 منشورات قصيرة ومميزة.
    3. قائمة بأقوى الهاشتاقات.
    4. نص بيع (Sales Copy) مقنع جداً.
    """

    try:
        # طلب الرد من OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini", # تأكد من استخدام موديل متاح في حسابك
            messages=[{"role": "user", "content": prompt}]
        )
        
        result = response.choices[0].message.content
        await waiting_msg.edit_text(result)
        
    except Exception as e:
        await waiting_msg.edit_text(f"❌ عذراً، حدث خطأ أثناء الاتصال بالذكاء الاصطناعي: {str(e)}")

# --- 4. تشغيل التطبيق ---
if __name__ == '__main__':
    # أ: تشغيل السيرفر الوهمي في خيط (Thread) منفصل
    threading.Thread(target=run_health_check_server, daemon=True).start()

    # ب: بناء وتشغيل بوت التليجرام
    if not TELEGRAM_BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN is not set!")
    else:
        app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

        # إضافة المعالجات (Handlers)
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

        print("Bot is starting polling...")
        app.run_polling()
