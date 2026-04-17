import os
import asyncio
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai

# 1. سيرفر وهمي لإبقاء الخدمة تعمل على Render
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is active")

def run_server():
    port = int(os.environ.get('PORT', 8080))
    httpd = HTTPServer(('0.0.0.0', port), HealthHandler)
    httpd.serve_forever()

# 2. إعداد Gemini
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

# 3. وظائف البوت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 أهلاً بك! أنا بوت Market Pilot. أرسل لي أي اسم منتج وسأقوم بتوليد إعلان له.")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    try:
        response = model.generate_content(f"صمم إعلان تسويقي قصير وجذاب لـ: {user_text}")
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text("عذراً، واجهت مشكلة صغيرة في معالجة طلبك.")

# 4. تشغيل كل شيء
if __name__ == '__main__':
    # تشغيل السيرفر في الخلفية
    threading.Thread(target=run_server, daemon=True).start()
    
    # تشغيل البوت بالطريقة الحديثة
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    application = Application.builder().token(token).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    
    print("Starting bot...")
    application.run_polling()
