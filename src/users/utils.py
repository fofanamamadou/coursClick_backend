import logging
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

# Une variable pour la génération des logg
logger = logging.getLogger(__name__)


def send_mail_html(subject:str, receivers:list, template:str, context:dict):
    """
    Cette fonction permet d'envoyer un mail à un utilisateur. Notre templates personnaliser. Les paramètres sont :
    - subject: Le Sujet ou l'objet du mail,
    - receivers: La liste des utilisateurs ou l'utilisateur auquel on envoie,
    - template: Notre template html personnalisé,
    - context: Le dictionnaire des variables qu'on souhaite envoyer dans le message
    """
    try:
        # Envoie du template HTML et les variables
        message = render_to_string(template, context)
        # Envoyer le mail
        send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list=receivers, fail_silently=True, html_message=message)
        # Connaître si la méthode a fonctionné avec Succès
        return True
    except Exception as e:
        logger.error(e)
        return False





