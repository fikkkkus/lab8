import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

# Загружаем переменные из .env
load_dotenv('params.env')

class EmailSender:
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_SERVER")
        self.smtp_port = os.getenv("SMTP_PORT")
        self.sender_email = os.getenv("EMAIL_ADDRESS")
        self.app_password = os.getenv("APP_PASSWORD")

    def send_email(self, recipient_email: str, message: str) -> bool:
        """Отправка email-сообщения через SMTP."""
        logging.info(f'Попытка отправить сообщение на адрес: {recipient_email}')

        try:
            with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port) as server:
                server.login(self.sender_email, self.app_password)

                email_message = MIMEMultipart()
                email_message['From'] = self.sender_email
                email_message['To'] = recipient_email
                email_message['Subject'] = "Сообщение от вашего Telegram-бота"
                email_message.attach(MIMEText(message, 'plain'))

                server.sendmail(self.sender_email, recipient_email, email_message.as_string())

            logging.info(f'Сообщение было успешно отправлено на {recipient_email}')
            return True

        except Exception as error:
            logging.error(f'Произошла ошибка при отправке на email: {error}')
            return False
