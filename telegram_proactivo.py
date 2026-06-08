import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_TOKEN = "8981973985:AAFi16NqNfEZiNJyIxJWcaij6WXsGnILOBI"
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Bot para enviar mensajes proactivos (iniciar conversación)
from telegram import Bot
bot = Bot(token=TELEGRAM_TOKEN)

async def iniciar_conversacion(chat_id: str, mensaje: str):
    """Permite al bot iniciar conversación."""
    await bot.send_message(chat_id=chat_id, text=mensaje)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    # Lógica de respuesta igual a la anterior
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": user_text}]
    )
    await update.message.reply_text(response.choices[0].message.content)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.run_polling()
