import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from google import genai
from datetime import datetime
from database import create_database, save_chat

# ==========================
# CONFIGURATION
# ==========================

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Create Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)


SYSTEM_PROMPT = """
You are Smart Assistant.

You were created by Rukyunus Ibnuyunus Olorunfemi using Python and the Telegram Bot API.

If someone asks:
- Who created you?
- Who is your founder?
- Who built you?

Answer:
"I was created by Rukyunus Ibnuyunus Olorunfemi."

You are friendly, intelligent and helpful.

Answer questions clearly and accurately.
"""

# ==========================
# COMMANDS
# ==========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hello! I'm Smart Assistant.\n\nAsk me anything."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Available commands:\n"
        "/start - Start the bot\n"
        "/help - Show this help message"
    )


# ==========================
# AI CHAT
# ==========================

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.message is None or update.message.text is None:
        return

    # ==========================
    # USER INFORMATION
    # ==========================

    user = update.effective_user

    user_id = user.id
    username = user.username if user.username else "No Username"
    first_name = user.first_name if user.first_name else "Unknown"

    # ==========================
    # USER MESSAGE
    # ==========================

    user_message = update.message.text

    prompt = SYSTEM_PROMPT + "\n\nUser: " + user_message

    try:
        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=prompt,
        )

        bot_response = response.text

        # Save successful conversation
        save_chat(
            user_id,
            username,
            first_name,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "SUCCESS",
            user_message,
            bot_response
        )

        # Reply to user
        await update.message.reply_text(bot_response)

    except Exception as e:
        print("ERROR:", repr(e))

        error = str(e)

        if "503" in error:
            bot_response = (
                "⚠️ The AI service is currently busy. Please try again in a few moments."
            )
            status = "FAILED (503 - Service Busy)"

        elif "429" in error:
            bot_response = (
                "⚠️ I've reached my current AI usage limit. Please try again later."
            )
            status = "FAILED (429 - Quota Exceeded)"

        else:
            bot_response = "❌ An unexpected error occurred."
            status = "FAILED (Unknown Error)"

        # Save failed conversation
        save_chat(
            user_id,
            username,
            first_name,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            status,
            user_message,
            bot_response
        )

        # Reply to user
        await update.message.reply_text(bot_response)


# ==========================
# CREATE DATABASE
# ==========================

create_database()

# ==========================
# CREATE BOT
# ==========================

app = Application.builder().token(TELEGRAM_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

print("🤖 Smart Assistant is running...")

app.run_polling()