import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import openai

# جلب المفاتيح من متغيرات البيئة في Render
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# إعداد عميل OpenAI (الطريقة الحديثة)
client = openai.OpenAI(api_key=OPENAI_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 أهلاً! أرسل منتجك وسأصنع لك حملة تسويق كاملة!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text

    prompt = f"""
    أنشئ حملة تسويق كاملة تشمل:
    - إعلان رئيسي
    - منشورات 3
    - هاشتاقات
    - نص بيع قوي
    
    المنتج: {user_input}
    """

    try:
        # استخدام الطريقة الصحيحة للإصدار الجديد من OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        
        result = response.choices[0].message.content
        await update.message.reply_text(result)
    except Exception as e:
        await update.message.reply_text(f"عذراً، حدث خطأ: {str(e)}")

if __name__ == '__main__':
    # بناء البوت
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # إضافة الأوامر والمستقبلات
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    # بدء التشغيل
    print("Bot is running...")
    app.run_polling()
