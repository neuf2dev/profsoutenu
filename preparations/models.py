from django.db import models
from django.conf import settings


class FichePreparation(models.Model):
    class Niveau(models.TextChoices):
        PS = 'PS', 'Petite Section'
        MS = 'MS', 'Moyenne Section'
        GS = 'GS', 'Grande Section'
        CP = 'CP', 'CP'
        CE1 = 'CE1', 'CE1'
        CE2 = 'CE2', 'CE2'
        CM1 = 'CM1', 'CM1'
        CM2 = 'CM2', 'CM2'
        SIX = '6E', '6ème'
        CINQ = '5E', '5ème'
        QUATRE = '4E', '4ème'
        TROIS = '3E', '3ème'
        SECONDE = '2NDE', 'Seconde'
        PREMIERE = '1ERE', 'Première'
        TERMINALE = 'TERM', 'Terminale'
        AUTRE = 'AUTRE', 'Autre niveau'

    class Matiere(models.TextChoices):
        FRANCAIS = 'FR', 'Français / Lettres'
        MATHS = 'MATHS', 'Mathématiques'
        HISTOIRE_GEO = 'HIST_GEO', 'Histoire - Géographie - EMC'
        SCIENCES = 'SCIENCES', 'Sciences et Technologie'
        SVT = 'SVT', 'Sciences de la Vie et de la Terre (SVT)'
        PC = 'PC', 'Physique - Chimie'
        EPS = 'EPS', 'Éducation Physique et Sportive'
        ARTS = 'ARTS', 'Arts Plastiques / Éducation Musicale'
        LANGUE = 'LV', 'Langues vivantes'
        PHILOSOPHIE = 'PHILO', 'Philosophie'
        SES = 'SES', 'Sciences Économiques et Sociales'
        NSI_TECH = 'NSI_TECH', 'Technologie / Numérique et Informatique (NSI)'
        AUTRE = 'AUTRE', 'Autre discipline'

    enseignant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='fiches_preparation',
        verbose_name="Enseignant"
    )

    titre = models.CharField(max_length=255, verbose_name="Titre de la séance")
    niveau = models.CharField(max_length=10, choices=Niveau.choices, default=Niveau.CM1)
    matiere = models.CharField(max_length=20, choices=Matiere.choices, default=Matiere.MATHS)
    theme = models.CharField(max_length=255, help_text="Ex: Les fractions simples, Le passé composé...")
    duree_minutes = models.PositiveIntegerField(default=45, verbose_name="Durée (min)")

    objectifs = models.TextField(blank=True, verbose_name="Objectifs pédagogiques")
    deroule_seance = models.TextField(blank=True, verbose_name="Déroulé de la séance (5 phases)")
    exercices_types = models.TextField(blank=True, verbose_name="Exercices d'application")

    date_creation = models.DateTimeField(auto_now_add=True)
    date_mise_a_jour = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Fiche de préparation"
        verbose_name_plural = "Fiches de préparation"
        ordering = ['-date_creation']

    def __str__(self):
        return f"{self.titre} - {self.get_niveau_display()} ({self.get_matiere_display()})"


class EvaluationQCM(models.Model):
    class Difficulte(models.TextChoices):
        FACILE = 'FACILE', 'Facile / Découverte'
        MOYEN = 'MOYEN', 'Intermédiaire / Standard'
        AVANCE = 'AVANCE', 'Avancé / Approfondissement'

    enseignant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='evaluations_qcm',
        verbose_name="Enseignant"
    )

    titre = models.CharField(max_length=255, verbose_name="Titre du QCM")
    niveau = models.CharField(max_length=10, choices=FichePreparation.Niveau.choices, default=FichePreparation.Niveau.CM1)
    matiere = models.CharField(max_length=20, choices=FichePreparation.Matiere.choices, default=FichePreparation.Matiere.MATHS)
    notions_cles = models.CharField(max_length=255, help_text="Ex: Accords participe passé, fractions équivalentes...")
    difficulte = models.CharField(max_length=10, choices=Difficulte.choices, default=Difficulte.MOYEN)
    nb_questions = models.PositiveIntegerField(default=5, verbose_name="Nombre de questions")

    contenu_eleve = models.TextField(blank=True, verbose_name="Sujet Élève (QCM)")
    contenu_corrige = models.TextField(blank=True, verbose_name="Corrigé Enseignant")
    pistes_remediation = models.TextField(blank=True, verbose_name="Pistes de remédiation & Différenciation")

    date_creation = models.DateTimeField(auto_now_add=True)
    date_mise_a_jour = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Évaluation QCM"
        verbose_name_plural = "Évaluations QCM"
        ordering = ['-date_creation']

    def __str__(self):
        return f"QCM: {self.titre} ({self.get_niveau_display()})"