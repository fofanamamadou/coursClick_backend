# Documentation - Nouvelle Structure d'Authentification

## Vue d'ensemble

La nouvelle structure d'authentification a été refactorisée pour améliorer la lisibilité, la maintenabilité et la sécurité du système de gestion des présences.

## Structure des fichiers

### `auth.py` - Logique d'authentification
Contient toutes les fonctions utilitaires pour l'authentification :
- `authenticate_admin()` - Authentification des administrateurs
- `authenticate_user()` - Authentification des utilisateurs (professeurs/étudiants)
- `generate_tokens()` - Génération des tokens JWT
- `get_user_permissions()` - Récupération des permissions selon le rôle
- `get_user_from_token()` - Extraction de l'utilisateur depuis le token
- `validate_password_strength()` - Validation de la force du mot de passe
- `can_user_login()` - Vérification des conditions de connexion

### `auth_views.py` - Vues d'authentification
Contient toutes les vues d'authentification :
- `admin_login_view` - Connexion administrateurs
- `user_login_view` - Connexion commune professeurs/étudiants
- `profile_view` - Profil utilisateur
- `logout_view` - Déconnexion
- `refresh_token_view` - Rafraîchissement des tokens
- `change_password_view` - Changement de mot de passe
- `forgot_password_view` - Demande de réinitialisation
- `reset_password_view` - Réinitialisation par lien
- `forgot_password_temp_view` - Mot de passe temporaire

## Endpoints disponibles

### Nouveaux endpoints (recommandés)
```
POST /auth/admin/login/          - Connexion administrateurs
POST /auth/user/login/           - Connexion professeurs/étudiants
GET  /auth/profile/              - Profil utilisateur
POST /auth/logout/               - Déconnexion
POST /auth/refresh/              - Rafraîchissement token
POST /auth/change-password/      - Changement mot de passe
POST /auth/forgot-password/      - Demande réinitialisation
POST /auth/reset-password/       - Réinitialisation par lien
POST /auth/forgot-password-temp/ - Mot de passe temporaire
```

### Anciens endpoints (compatibilité)
```
POST /admin/login/    - Connexion admin (ancienne version)
POST /login/          - Connexion user (ancienne version)
POST /logout/         - Déconnexion (ancienne version)
POST /token/refresh/  - Refresh token (ancienne version)
```

## Utilisation

### 1. Connexion Administrateur
```bash
POST /auth/admin/login/
{
    "email": "admin@example.com",
    "password": "motdepasse"
}
```

**Réponse :**
```json
{
    "success": true,
    "message": "Connexion administrateur réussie",
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user_type": "superuser",
    "permissions": {
        "is_admin": true,
        "can_manage_users": true,
        "can_view_planning": true,
        "can_create_planning": true,
        "can_manage_absences": true,
        "can_view_statistics": true,
        "can_manage_system": true
    },
    "token_type": "Bearer",
    "expires_in": 86400,
    "user": {
        "id": 1,
        "email": "admin@example.com",
        "first_name": "Admin",
        "last_name": "User",
        "is_superuser": true,
        "is_staff": true
    }
}
```

### 2. Connexion Utilisateur (Professeur/Étudiant)
```bash
POST /auth/user/login/
{
    "email": "professeur@example.com",
    "password": "motdepasse"
}
```

**Réponse :**
```json
{
    "success": true,
    "message": "Connexion professor réussie",
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user_type": "professor",
    "roles": ["PROFESSOR"],
    "permissions": {
        "is_professor": true,
        "can_view_planning": true,
        "can_create_planning": true,
        "can_manage_absences": true,
        "can_view_statistics": true
    },
    "token_type": "Bearer",
    "expires_in": 86400,
    "user": {
        "id": 2,
        "email": "professeur@example.com",
        "first_name": "Jean",
        "last_name": "Dupont",
        "modules": [1, 2, 3],
        "roles_details": [{"name": "PROFESSOR"}]
    }
}
```

### 3. Récupération du profil
```bash
GET /auth/profile/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

### 4. Changement de mot de passe
```bash
POST /auth/change-password/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
{
    "current_password": "ancien_mot_de_passe",
    "new_password": "nouveau_mot_de_passe"
}
```

### 5. Déconnexion
```bash
POST /auth/logout/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 6. Rafraîchissement du token
```bash
POST /auth/refresh/
{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 7. Réinitialisation du mot de passe
```bash
# Demande de réinitialisation
POST /auth/forgot-password/
{
    "email": "user@example.com"
}

# Réinitialisation avec le lien reçu
POST /auth/reset-password/
{
    "uidb64": "MQ",
    "token": "abc123-def456-ghi789",
    "new_password": "nouveau_mot_de_passe"
}
```

## Types d'utilisateurs et permissions

### Administrateur (is_staff=True ou is_superuser=True)
- Accès complet au système
- Gestion des utilisateurs
- Création et modification des plannings
- Gestion des absences
- Accès aux statistiques
- Gestion du système

### Professeur (role=PROFESSOR)
- Consultation des plannings
- Création de plannings pour ses modules
- Gestion des absences de ses étudiants
- Consultation des statistiques de ses cours

### Étudiant (role=STUDENT)
- Consultation de son planning
- Pointage des présences
- Consultation de ses absences

## Sécurité

### Validation des mots de passe
- Minimum 8 caractères
- Extensible pour ajouter d'autres règles

### Gestion des erreurs
- Messages d'erreur standardisés
- Logging des tentatives de connexion
- Protection contre la divulgation d'informations

### Tokens JWT
- Expiration : 24 heures
- Blacklisting des refresh tokens à la déconnexion
- Validation automatique de l'état actif de l'utilisateur

## Migration depuis l'ancienne structure

1. **Compatibilité** : Les anciens endpoints restent fonctionnels
2. **Transition progressive** : Migrez vos applications frontend vers les nouveaux endpoints
3. **Suppression** : Une fois la migration terminée, vous pourrez supprimer les anciens endpoints

## Configuration requise

Assurez-vous d'avoir ces paramètres dans votre `settings.py` :

```python
# Email configuration (pour la réinitialisation de mot de passe)
DEFAULT_FROM_EMAIL = 'noreply@votre-domaine.com'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # ou votre serveur SMTP
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'votre-email@gmail.com'
EMAIL_HOST_PASSWORD = 'votre-mot-de-passe-app'

# URL du frontend (pour les liens de réinitialisation)
FRONTEND_URL = 'http://localhost:3000'  # ou votre URL de production

# JWT Configuration
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}
```

## Tests

Pour tester la nouvelle structure d'authentification, vous pouvez utiliser les endpoints avec curl ou Postman. Assurez-vous que :

1. Les connexions admin et utilisateur fonctionnent séparément
2. Les permissions sont correctement appliquées
3. La réinitialisation de mot de passe fonctionne
4. Les tokens sont correctement gérés

## Support

Pour toute question ou problème avec la nouvelle structure d'authentification, consultez les logs de l'application ou contactez l'équipe de développement.
