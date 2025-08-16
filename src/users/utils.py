import logging
import threading
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

class EmailThread(threading.Thread):
    def __init__(self, subject, message, receivers):
        self.subject = subject
        self.message = message
        self.receivers = receivers
        threading.Thread.__init__(self)

    def run(self):
        try:
            send_mail(
                self.subject,
                self.message,
                settings.EMAIL_HOST_USER,
                recipient_list=self.receivers,
                fail_silently=False,
                html_message=self.message
            )
            logger.info(f"Email sent successfully to {self.receivers}")
        except Exception as e:
            logger.error(f"Error sending email to {self.receivers}: {e}")

def send_mail_html(subject: str, receivers: list, template: str, context: dict):
    """
    Cette fonction permet d'envoyer un mail à un utilisateur en utilisant un thread.
    """
    message = render_to_string(template, context)
    email_thread = EmailThread(subject, message, receivers)
    email_thread.start()
    return True