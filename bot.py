import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)

SYSTEM_PROMPT = os.environ.get(
    "SYSTEM_PROMPT",
    "Ты — полноправный и живой участник нашего группового чата в Telegram. Отвечай кратко, общайся непринужденно, с юмором и иронией."
)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_text = update.message.text
    user_name = update.message.from_user.first_name or "Участник"

    try:
        response = client.chat.completions.create(
            model="google/gemini-2.5-flash:free",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"{user_name}: {user_text}"}
            ],
            max_tokens=300
        )
        
        bot_reply = response.choices[0].message.content
        if bot_reply:
            await update.message.reply_text(bot_reply)

    except Exception as e:
        print(f"Ошибка при запросе к ИИ: {e}")

def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        print("Ошибка: Не задан TELEGRAM_BOT_TOKEN!")
        return


    proxy_url = os.environ.get("HTTP_PROXY")
    builder = Application.builder().token(token)
    if proxy_url:
        builder = builder.proxy(proxy_url).get_updates_proxy(proxy_url)
    app = builder.build()
    
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Бот успешно запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
