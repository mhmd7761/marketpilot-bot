import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import openai
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# سيرفر وهمي لإرضاء Render
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_health_check():
    server = HTTPServer(('0.0.0.0', int(os.environ.get('PORT', 8080))), HealthCheckHandler)
    server.serve_forever()

# إعدادات البوت
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=OPENAI_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 أهلاً بك! أنا بوت التسويق الذكي، كيف أساعدك اليوم؟")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    prompt = f"أنشئ حملة تسويقية لـ: {user_input}"
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        await update.message.reply_text(response.choices[0].message.content)
    except Exception as e:
        await update.message.reply_text(f"خطأ: {str(e)}")

if __name__ == '__main__':
    # تشغيل السيرفر الوهمي في خلفية الكود
    threading.Thread(target=run_health_check, daemon=True).start()

    # تشغيل البوت
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Bot and Health Check are running...")
    app.run_polling()
