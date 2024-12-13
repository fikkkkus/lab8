import re

class EmailValidator:
    def __init__(self):
        self.email_regex = r'^[\w\.-]+@([\w-]+\.)+[\w-]{2,4}$'

    def validate(self, email_address: str) -> bool:
        """Проверка формата email-адреса."""
        return re.match(self.email_regex, email_address) is not None
