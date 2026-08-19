import os
import json
import re
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Charger le fichier .env
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / '.env')


def get_genai_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY non trouvée dans le fichier .env.")
    return genai.Client(api_key=api_key)


def _nettoyer_json(texte):
    """Extrait le JSON même si le modèle l'entoure de balises markdown."""
    texte = texte.strip()
    match = re.search(r'\{.*\}', texte, re.DOTALL)
    if match:
        return match.group(0)
    return texte


def generer_contenu_fiche(titre, niveau_label, matiere_label, theme, duree):
    prompt = f"""
Tu es un conseiller pédagogique expert de l'Éducation nationale française.
Rédige le contenu d'une fiche de préparation de séance officielle pour un enseignant.

Informations sur la séance :
- Titre : {titre}
- Niveau : {niveau_label}
- Matière : {matiere_label}
- Thème / Notion : {theme}
- Durée : {duree} minutes

Consignes de rédaction :
1. "objectifs" : Objectifs d'apprentissage clairs, compétences visées et repères du socle commun.
2. "deroule_seance" : Le déroulé complet structuré selon les 5 phases institutionnelles :
   - Phase 1 : Découverte / Accroche
   - Phase 2 : Recherche / Manipulation
   - Phase 3 : Mise en commun & Institutionnalisation (trace écrite)
   - Phase 4 : Entraînement / Application
   - Phase 5 : Bilan / Clôture
3. "exercices_types" : Des exemples concrets d'exercices d'application avec critères d'évaluation formative.

Réponds STRICTEMENT au format JSON valide avec ces 3 clés :
{{
  "objectifs": "texte...",
  "deroule_seance": "texte...",
  "exercices_types": "texte..."
}}
"""
    try:
        client = get_genai_client()
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.7,
            ),
        )
        data_clean = _nettoyer_json(response.text)
        return json.loads(data_clean)
    except Exception as e:
        print(f"\n--- ERREUR GEMINI FICHE ---\n{e}\n---------------------------\n")
        return {
            "objectifs": "Erreur lors de la génération automatique des objectifs.",
            "deroule_seance": "Erreur lors de la génération automatique du déroulé.",
            "exercices_types": "Erreur lors de la génération automatique des exercices."
        }


def generer_contenu_qcm(titre, niveau_label, matiere_label, notions_cles, difficulte_label, nb_questions):
    prompt = f"""
Tu es un conseiller pédagogique expert de l'Éducation nationale française.
Conçois une évaluation formative complète sous forme de QCM.

Informations :
- Titre : {titre}
- Niveau : {niveau_label}
- Matière : {matiere_label}
- Notions ciblées : {notions_cles}
- Niveau de difficulté : {difficulte_label}
- Nombre de questions : {nb_questions}

Consignes de rédaction :
1. "contenu_eleve" :
   - Présentation sobre et claire prête à imprimer.
   - Les {nb_questions} questions numérotées avec chacune 4 propositions (A, B, C, D) et des cases à cocher [ ].
   - Ne JAMAIS indiquer les réponses dans cette section.
2. "contenu_corrige" :
   - Reprendre chaque question avec la bonne réponse clairement identifiée.
   - Fournir une brève explication didactique pour chaque réponse.
   - Proposer un barème simple sur 20 points.
3. "pistes_remediation" :
   - Analyse des erreurs fréquentes probables des élèves sur ces questions.
   - Conseils pratiques pour l'enseignant pour organiser la remédiation en classe entière ou en petits groupes.
   - Pistes de différenciation pédagogique.

Réponds STRICTEMENT au format JSON valide avec ces 3 clés :
{{
  "contenu_eleve": "texte...",
  "contenu_corrige": "texte...",
  "pistes_remediation": "texte..."
}}
"""
    try:
        client = get_genai_client()
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.7,
            ),
        )
        data_clean = _nettoyer_json(response.text)
        return json.loads(data_clean)
    except Exception as e:
        print(f"\n--- ERREUR GEMINI QCM ---\n{e}\n-------------------------\n")
        return {
            "contenu_eleve": "Erreur lors de la génération du sujet élève.",
            "contenu_corrige": "Erreur lors de la génération du corrigé.",
            "pistes_remediation": "Erreur lors de la génération des pistes de remédiation."
        }