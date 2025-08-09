import logging
from django.utils import timezone

from .models import Absence
from planning.models import Planning
from pointage.models import Pointage, SessionPresence
from users.models import User

logger = logging.getLogger(__name__)

def generer_absences_pour_planning(planning: Planning) -> dict:
    """
    Génère les absences pour une instance de Planning donnée.

    Args:
        planning: L'objet Planning pour lequel générer les absences.

    Returns:
        Un dictionnaire contenant les résultats de l'opération.
    """
    # Évite de générer deux fois les absences
    if Absence.objects.filter(planning=planning).exists():
        logger.info(f"Les absences pour le planning #{planning.id} ont déjà été générées.")
        return {"message": "Déjà généré", "absences_creees": 0}

    logger.info(f"Traitement du planning #{planning.id} pour le cours de {planning.module.name}...")

    # **CETTE LOGIQUE DEVRA ÊTRE ADAPTÉE PRÉCISÉMENT À VOTRE STRUCTURE**
    classe = planning.user.classe  # Hypothèse simplifiée
    if not classe:
        logger.warning(f"Impossible de déterminer la classe pour le planning #{planning.id}. On ignore.")
        return {"message": "Classe non trouvée", "absences_creees": 0}

    etudiants_de_la_classe = User.objects.filter(classe=classe, roles__name='STUDENT')
    sessions_presence = SessionPresence.objects.filter(planning=planning)
    etudiants_presents_ids = Pointage.objects.filter(session__in=sessions_presence).values_list('user_id', flat=True)
    etudiants_absents = etudiants_de_la_classe.exclude(id__in=etudiants_presents_ids)

    absences_creees = 0
    for etudiant in etudiants_absents:
        _, created = Absence.objects.get_or_create(user=etudiant, planning=planning)
        if created:
            absences_creees += 1

    logger.info(f">>> {absences_creees} absence(s) créée(s) pour le planning #{planning.id}.")
    
    return {
        "message": "Opération terminée",
        "absences_creees": absences_creees,
        "etudiants_presents": etudiants_presents_ids.count(),
        "etudiants_absents": etudiants_absents.count()
    }
