import os
from dotenv import load_dotenv
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

import src.helpers.openai_helper as openai_helper
import src.helpers.logging_helper as logging_helper

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', 'config', '.env'))

logger = logging_helper.get_logger()

class Dispatcher:
    def __init__(self):
        self.bot_token = os.getenv("ENV_BOT_KEY")
        self.bot = Bot(self.bot_token)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = update.message
        if message.voice:
            # Handle voice message
            file = await self.bot.get_file(message.voice.file_id)
            file_path = "voice_message.ogg"
            await file.download_to_drive(file_path)
            text = openai_helper.transcribe_audio(file_path)
        elif message.text:
            # Handle text message
            text = message.text
        else:
            await message.reply_text("Unsupported message type.")
            return

        # response_text = openai_helper.generate_text(text)
        response_text = "You said: " + text
        await message.reply_text(response_text)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Hello! I am your assistant bot. Send me a text or voice message.")

def main():
    dispatcher = Dispatcher()
    application = ApplicationBuilder().token(dispatcher.bot_token).build()

    start_handler = CommandHandler('start', dispatcher.start)
    message_handler = MessageHandler(filters.TEXT | filters.VOICE, dispatcher.handle_message)

    application.add_handler(start_handler)
    application.add_handler(message_handler)

    application.run_polling()

if __name__ == "__main__":
    main()
