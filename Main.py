import os
import logging
import openai
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    ContextTypes, MessageHandler, filters
)


# Load API keys from environment
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY


# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


# Chat history to add memory
chat_histories = {}


# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hey bestie! 💬 I'm your personal buddy bot 🤖 — "
        "here to flirt, chat, or give love advice. Just message me or type /help ❤️"
    )


# Help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Here's what I can do:\n\n"
        "💌 Just type anything and I'll chat like your bestie!\n"
        "😏 /flirt — Wanna flirt a little?\n"
        "📝 /history — View recent convos\n"
        "🚀 More features coming soon!"
    )


# Flirt command
async def flirt_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    flirty_lines = [
        "If I had a rose 🌹 for every time I thought of you, I'd be walking through a garden forever 😘",
        "Are you French? Because Eiffel for you 😏",
        "Do you have a map? I just got lost in your eyes 💫",
        "You're my favorite notification 💖",
    ]
    import random
    await update.message.reply_text(random.choice(flirty_lines))


# History command
async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    history = chat_histories.get(user_id, [])
    if not history:
        await update.message.reply_text("No juicy history yet... Let’s make some 💕")
    else:
        formatted = "\n\n".join(
            f"You: {m['content']}" if m['role'] == 'user' else f"Bot: {m['content']}"
            for m in history[-5:]
        )
        await update.message.reply_text(f"Here's our recent chat 💬:\n\n{formatted}")


# Message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_input = update.message.text


    # Initialize history
    if user_id not in chat_histories:
        chat_histories[user_id] = []


    chat_histories[user_id].append({"role": "user", "content": user_input})
    history = chat_histories[user_id][-10:]  # Keep last 10 messages


    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You're a flirty, supportive, funny best friend who gives relationship advice in a casual tone."},
                *history
            ]
        )
        reply = response.choices[0].message.content.strip()
        chat_histories[user_id].append({"role": "assistant", "content": reply})
        await update.message.reply_text(reply)


    except Exception as e:
        logging.error(f"OpenAI error: {e}")
        await update.message.reply_text("Oops! Something went wrong. 🤕")


# Main function
async def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()


    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("flirt", flirt_command))
    app.add_handler(CommandHandler("history", history_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))


    print("Bot is running... 🚀")
    await app.run_polling()


# Run
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())