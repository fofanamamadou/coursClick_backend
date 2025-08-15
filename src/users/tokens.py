from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import timezone
from datetime import timedelta

class CustomPasswordResetTokenGenerator(PasswordResetTokenGenerator):
    """
    Générateur de token personnalisé avec expiration de 5 minutes
    """
    pass

# Instance du générateur personnalisé
password_reset_token_generator = CustomPasswordResetTokenGenerator()
