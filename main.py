import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai

# --- السيرفر الوهمي لـ Render ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Bot is Live with Gemini!")

def run_health_check_server():
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# --- إعداد Gemini ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash') # موديل سريع ومجاني

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 مرحباً! أنا بوت Market Pilot مدعوم بذكاء Gemini. أرسل اسم منتجك الآن!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    waiting_msg = await update.message.reply_text("⏳ جاري التفكير باستخدام Gemini...")

    prompt = f"أنت خبير تسويق. صمم حملة تسويقية كاملة لمنتج: {user_input}. تشمل إعلان، منشورات، وهاشتاقات."

    try:
        response = model.generate_content(prompt)
        await waiting_msg.edit_text(response.text)
    except Exception as e:
        await waiting_msg.edit_text(f"❌ خطأ: {str(e)}")

if __name__ == '__main__':
    threading.Thread(target=run_health_check_server, daemon=True).start()
    
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("Bot is running with Gemini...")
    app.run_polling()
