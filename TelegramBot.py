import logging
import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import EmailValidator
import EmailSender

from EmailSender import EmailSender
from EmailValidator import EmailValidator

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")
load_dotenv('params.env')

class TelegramBot:
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.email_sender = EmailSender()
        self.email_validator = EmailValidator()
        self.user_sessions = {}

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Инициализация сессии пользователя и приветствие."""
        user_id = update.effective_user.id
        logging.info(f'Пользователь с ID {user_id} начал взаимодействие с ботом')
        self.user_sessions[user_id] = {'email': None, 'message': None}
        await update.message.reply_text("Здравствуйте! Пожалуйста, отправьте свой email для начала.")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений от пользователя."""
        user_id = update.effective_user.id
        message_text = update.message.text

        if user_id not in self.user_sessions:
            await update.message.reply_text("Для начала введите /start.")
            return

        if self.user_sessions[user_id]['email'] is None:
            await self._handle_email_input(update, user_id, message_text)
        elif self.user_sessions[user_id]['message'] is None:
            await self._handle_message_input(update, user_id, message_text)

    async def _handle_email_input(self, update: Update, user_id: int, email_input: str):
        """Обработка ввода email."""
        logging.info(f'Пользователь с ID {user_id} вводит email: {email_input}')

        if self.email_validator.validate(email_input):
            self.user_sessions[user_id]['email'] = email_input
            await update.message.reply_text("Хорошо! Отправьте текст сообщения.")
        else:
            await update.message.reply_text("Указанный email неверный. Попробуйте снова.")
            logging.warning(f'Некорректный email: "{email_input}" для пользователя с ID {user_id}')

    async def _handle_message_input(self, update: Update, user_id: int, message_input: str):
        """Обработка ввода текстового сообщения."""
        self.user_sessions[user_id]['message'] = message_input
        user_email = self.user_sessions[user_id]['email']

        if self.email_sender.send_email(user_email, message_input):
            await update.message.reply_text("Ваше сообщение было успешно отправлено!")
        else:
            await update.message.reply_text("Не удалось отправить сообщение. Попробуйте еще раз.")

        # Очистка сессии пользователя
        del self.user_sessions[user_id]

    def run(self):
        """Запуск бота."""
        app = Application.builder().token(self.bot_token).build()

        app.add_handler(CommandHandler("start", self.start_command))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

        logging.info("Бот успешно запущен и готов к работе...")
        app.run_polling()

TeloBot = TelegramBot(os.getenv("TG_BOT_TOKEN"))
TeloBot.run()