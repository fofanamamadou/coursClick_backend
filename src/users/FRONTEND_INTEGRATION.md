# Guide d'intégration Frontend - Réinitialisation de mot de passe

## Configuration Backend

### 1. Configuration dans `settings.py`

Ajoutez cette configuration dans votre fichier `settings.py` :

```python
# URL du frontend pour les liens de réinitialisation
FRONTEND_URL = 'http://localhost:3000'  # En développement
# FRONTEND_URL = 'https://votre-domaine.com'  # En production

# Configuration email (obligatoire pour l'envoi des emails)
DEFAULT_FROM_EMAIL = 'noreply@votre-domaine.com'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # ou votre serveur SMTP
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'votre-email@gmail.com'
EMAIL_HOST_PASSWORD = 'votre-mot-de-passe-app'
```

## Flux de réinitialisation de mot de passe

### Étape 1 : Demande de réinitialisation (Frontend)

L'utilisateur saisit son email sur une page "Mot de passe oublié" :

```javascript
// Exemple avec fetch (JavaScript vanilla)
async function requestPasswordReset(email) {
    try {
        const response = await fetch('/auth/forgot-password/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email: email })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('Un email de réinitialisation a été envoyé si votre adresse existe.');
        } else {
            alert('Erreur: ' + data.error);
        }
    } catch (error) {
        console.error('Erreur:', error);
        alert('Une erreur est survenue');
    }
}
```

### Étape 2 : Email envoyé automatiquement

Le backend envoie automatiquement un email avec un lien de ce format :
```
http://localhost:3000/reset-password/MQ/abc123-def456-ghi789/
```

Structure du lien :
- `MQ` = uidb64 (ID utilisateur encodé en base64)
- `abc123-def456-ghi789` = token de réinitialisation

### Étape 3 : Page de réinitialisation (Frontend)

Créez une route dans votre frontend pour capturer ce lien :

#### React Router exemple :
```javascript
// App.js ou votre fichier de routes
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import ResetPasswordPage from './components/ResetPasswordPage';

function App() {
    return (
        <Router>
            <Routes>
                {/* Autres routes */}
                <Route path="/reset-password/:uidb64/:token" element={<ResetPasswordPage />} />
            </Routes>
        </Router>
    );
}
```

#### Vue.js Router exemple :
```javascript
// router/index.js
const routes = [
    // Autres routes
    {
        path: '/reset-password/:uidb64/:token',
        name: 'ResetPassword',
        component: () => import('@/views/ResetPasswordPage.vue')
    }
];
```

### Étape 4 : Composant de réinitialisation

#### Exemple React :
```javascript
// components/ResetPasswordPage.js
import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

function ResetPasswordPage() {
    const { uidb64, token } = useParams();
    const navigate = useNavigate();
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        if (password !== confirmPassword) {
            alert('Les mots de passe ne correspondent pas');
            return;
        }

        if (password.length < 8) {
            alert('Le mot de passe doit contenir au moins 8 caractères');
            return;
        }

        setLoading(true);

        try {
            const response = await fetch('/auth/reset-password/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    uidb64: uidb64,
                    token: token,
                    new_password: password
                })
            });

            const data = await response.json();

            if (data.success) {
                alert('Mot de passe réinitialisé avec succès !');
                navigate('/login'); // Rediriger vers la page de connexion
            } else {
                alert('Erreur: ' + data.error);
            }
        } catch (error) {
            console.error('Erreur:', error);
            alert('Une erreur est survenue');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="reset-password-page">
            <h2>Réinitialiser votre mot de passe</h2>
            <form onSubmit={handleSubmit}>
                <div>
                    <label>Nouveau mot de passe :</label>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                        minLength={8}
                    />
                </div>
                <div>
                    <label>Confirmer le mot de passe :</label>
                    <input
                        type="password"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        required
                        minLength={8}
                    />
                </div>
                <button type="submit" disabled={loading}>
                    {loading ? 'Réinitialisation...' : 'Réinitialiser'}
                </button>
            </form>
        </div>
    );
}

export default ResetPasswordPage;
```

#### Exemple Vue.js :
```vue
<!-- views/ResetPasswordPage.vue -->
<template>
  <div class="reset-password-page">
    <h2>Réinitialiser votre mot de passe</h2>
    <form @submit.prevent="handleSubmit">
      <div>
        <label>Nouveau mot de passe :</label>
        <input
          v-model="password"
          type="password"
          required
          minlength="8"
        />
      </div>
      <div>
        <label>Confirmer le mot de passe :</label>
        <input
          v-model="confirmPassword"
          type="password"
          required
          minlength="8"
        />
      </div>
      <button type="submit" :disabled="loading">
        {{ loading ? 'Réinitialisation...' : 'Réinitialiser' }}
      </button>
    </form>
  </div>
</template>

<script>
export default {
  name: 'ResetPasswordPage',
  data() {
    return {
      password: '',
      confirmPassword: '',
      loading: false
    };
  },
  methods: {
    async handleSubmit() {
      if (this.password !== this.confirmPassword) {
        alert('Les mots de passe ne correspondent pas');
        return;
      }

      if (this.password.length < 8) {
        alert('Le mot de passe doit contenir au moins 8 caractères');
        return;
      }

      this.loading = true;

      try {
        const response = await fetch('/auth/reset-password/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            uidb64: this.$route.params.uidb64,
            token: this.$route.params.token,
            new_password: this.password
          })
        });

        const data = await response.json();

        if (data.success) {
          alert('Mot de passe réinitialisé avec succès !');
          this.$router.push('/login');
        } else {
          alert('Erreur: ' + data.error);
        }
      } catch (error) {
        console.error('Erreur:', error);
        alert('Une erreur est survenue');
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>
```

## Gestion des erreurs

### Erreurs possibles du backend :

1. **Lien invalide** : `"Lien invalide"`
2. **Lien expiré** : `"Lien de réinitialisation invalide ou expiré"`
3. **Mot de passe faible** : `"Le mot de passe doit contenir au moins 8 caractères"`
4. **Données manquantes** : `"uidb64, token et new_password sont requis"`

### Gestion côté frontend :
```javascript
// Exemple de gestion d'erreurs plus robuste
const handleResetPassword = async (uidb64, token, newPassword) => {
    try {
        const response = await fetch('/auth/reset-password/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                uidb64,
                token,
                new_password: newPassword
            })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            return { success: true, message: data.message };
        } else {
            return { success: false, error: data.error || 'Erreur inconnue' };
        }
    } catch (error) {
        return { success: false, error: 'Erreur de connexion' };
    }
};
```

## Sécurité

### Bonnes pratiques :

1. **Validation côté frontend** : Vérifiez la force du mot de passe
2. **HTTPS obligatoire** : En production, utilisez toujours HTTPS
3. **Expiration des liens** : Les liens expirent automatiquement après 24h
4. **Rate limiting** : Implémentez une limitation des tentatives
5. **Logs de sécurité** : Surveillez les tentatives de réinitialisation

### Exemple de validation de mot de passe :
```javascript
function validatePassword(password) {
    const errors = [];
    
    if (password.length < 8) {
        errors.push('Au moins 8 caractères');
    }
    
    if (!/[A-Z]/.test(password)) {
        errors.push('Au moins une majuscule');
    }
    
    if (!/[a-z]/.test(password)) {
        errors.push('Au moins une minuscule');
    }
    
    if (!/[0-9]/.test(password)) {
        errors.push('Au moins un chiffre');
    }
    
    return {
        isValid: errors.length === 0,
        errors: errors
    };
}
```

## Test de l'intégration

### 1. Test manuel :
1. Allez sur votre page "Mot de passe oublié"
2. Saisissez un email valide
3. Vérifiez la réception de l'email
4. Cliquez sur le lien dans l'email
5. Saisissez un nouveau mot de passe
6. Vérifiez que vous pouvez vous connecter avec le nouveau mot de passe

### 2. Test automatisé (exemple Jest) :
```javascript
// __tests__/ResetPassword.test.js
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import ResetPasswordPage from '../components/ResetPasswordPage';

// Mock fetch
global.fetch = jest.fn();

test('should reset password successfully', async () => {
    fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, message: 'Mot de passe réinitialisé' })
    });

    render(
        <BrowserRouter>
            <ResetPasswordPage />
        </BrowserRouter>
    );

    fireEvent.change(screen.getByLabelText(/nouveau mot de passe/i), {
        target: { value: 'nouveauMotDePasse123' }
    });

    fireEvent.change(screen.getByLabelText(/confirmer/i), {
        target: { value: 'nouveauMotDePasse123' }
    });

    fireEvent.click(screen.getByRole('button', { name: /réinitialiser/i }));

    await waitFor(() => {
        expect(fetch).toHaveBeenCalledWith('/auth/reset-password/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                uidb64: expect.any(String),
                token: expect.any(String),
                new_password: 'nouveauMotDePasse123'
            })
        });
    });
});
```

## Résumé des endpoints

```
POST /auth/forgot-password/     # Demande de réinitialisation
POST /auth/reset-password/      # Réinitialisation avec lien
```

Cette intégration vous permet d'avoir un système de réinitialisation de mot de passe sécurisé et professionnel !
