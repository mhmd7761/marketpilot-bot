import os
import asyncio
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai

# سيرفر بسيط لمنع Render من إيقاف الخدمة
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot Active")

def run_health_server():
    port = int(os.environ.get('PORT', 8080))
    HTTPServer(('0.0.0.0', port), HealthHandler).serve_forever()

# إعداد ذكاء Gemini الاصطناعي
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 أهلاً بك! أرسل اسم منتجك وسأقوم بتصميم حملة تسويقية لك.")

async def handle_marketing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        response = model.generate_content(f"أنشئ إعلان تسويقي قصير وجذاب لـ: {update.message.text}")
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text("⏳ حدث ضغط بسيط، حاول مرة أخرى.")

if __name__ == '__main__':
    # تشغيل السيرفر في خلفية النظام
    threading.Thread(target=run_health_server, daemon=True).start()
    
    # تشغيل البوت باستخدام Application مباشرة (الطريقة الأضمن للإصدار 20.8)
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    app = Application.builder().token(token).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_marketing))
    
    print("Bot is starting...")
    app.run_polling()
