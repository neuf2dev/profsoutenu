import io
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Q
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from .models import FichePreparation, EvaluationQCM
from .forms import InscriptionForm, FichePreparationForm, FicheEditionForm, EvaluationQCMForm
from .services import generer_contenu_fiche, generer_contenu_qcm


def inscription_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Bienvenue sur ProfSoutenu, {user.username} !")
            return redirect('dashboard')
    else:
        form = InscriptionForm()
    return render(request, 'registration/inscription.html', {'form': form})


@login_required
def dashboard_view(request):
    search_query = request.GET.get('q', '').strip()
    niveau_filter = request.GET.get('niveau', '').strip()
    matiere_filter = request.GET.get('matiere', '').strip()

    # Requêtes pour les fiches de préparation
    fiches_qs = FichePreparation.objects.filter(enseignant=request.user)
    if search_query:
        fiches_qs = fiches_qs.filter(
            Q(titre__icontains=search_query) | Q(theme__icontains=search_query)
        )
    if niveau_filter:
        fiches_qs = fiches_qs.filter(niveau=niveau_filter)
    if matiere_filter:
        fiches_qs = fiches_qs.filter(matiere=matiere_filter)

    # Requêtes pour les QCM
    qcms_qs = EvaluationQCM.objects.filter(enseignant=request.user)
    if search_query:
        qcms_qs = qcms_qs.filter(
            Q(titre__icontains=search_query) | Q(notions_cles__icontains=search_query)
        )
    if niveau_filter:
        qcms_qs = qcms_qs.filter(niveau=niveau_filter)
    if matiere_filter:
        qcms_qs = qcms_qs.filter(matiere=matiere_filter)

    context = {
        'fiches': fiches_qs,
        'qcms': qcms_qs,
        'search_query': search_query,
        'niveau_filter': niveau_filter,
        'matiere_filter': matiere_filter,
        'niveaux': FichePreparation.Niveau.choices,
        'matieres': FichePreparation.Matiere.choices,
    }
    return render(request, 'preparations/dashboard.html', context)


# ==========================================
# MODULE 1 : FICHES DE PRÉPARATION
# ==========================================

@login_required
def creer_fiche_view(request):
    if request.method == 'POST':
        form = FichePreparationForm(request.POST)
        if form.is_valid():
            fiche = form.save(commit=False)
            fiche.enseignant = request.user

            contenu_ia = generer_contenu_fiche(
                titre=fiche.titre,
                niveau_label=fiche.get_niveau_display(),
                matiere_label=fiche.get_matiere_display(),
                theme=fiche.theme,
                duree=fiche.duree_minutes
            )

            fiche.objectifs = contenu_ia.get('objectifs', '')
            fiche.deroule_seance = contenu_ia.get('deroule_seance', '')
            fiche.exercices_types = contenu_ia.get('exercices_types', '')
            fiche.save()

            messages.success(request, "Fiche de préparation générée avec succès !")
            return redirect('detail_fiche', pk=fiche.pk)
    else:
        form = FichePreparationForm()
    return render(request, 'preparations/creer_fiche.html', {'form': form})


@login_required
def detail_fiche_view(request, pk):
    fiche = get_object_or_404(FichePreparation, pk=pk, enseignant=request.user)
    return render(request, 'preparations/detail_fiche.html', {'fiche': fiche})


@login_required
def editer_fiche_view(request, pk):
    fiche = get_object_or_404(FichePreparation, pk=pk, enseignant=request.user)
    if request.method == 'POST':
        form = FicheEditionForm(request.POST, instance=fiche)
        if form.is_valid():
            form.save()
            messages.success(request, "Modifications enregistrées.")
            return redirect('detail_fiche', pk=fiche.pk)
    else:
        form = FicheEditionForm(instance=fiche)
    return render(request, 'preparations/editer_fiche.html', {'form': form, 'fiche': fiche})


@login_required
def supprimer_fiche_view(request, pk):
    fiche = get_object_or_404(FichePreparation, pk=pk, enseignant=request.user)
    if request.method == 'POST':
        fiche.delete()
        messages.success(request, "Fiche supprimée avec succès.")
        return redirect('dashboard')
    return render(request, 'preparations/supprimer_fiche.html', {'fiche': fiche})


@login_required
def exporter_pdf_fiche_view(request, pk):
    fiche = get_object_or_404(FichePreparation, pk=pk, enseignant=request.user)
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'MainTitle',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#1E3A8A"),
        spaceAfter=12
    )
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#1E40AF"),
        spaceBefore=12,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#334155")
    )

    story = []
    story.append(Paragraph(fiche.titre, title_style))
    story.append(Spacer(1, 6))

    meta_data = [
        [
            Paragraph(f"<b>Niveau :</b> {fiche.get_niveau_display()}", body_style),
            Paragraph(f"<b>Matière :</b> {fiche.get_matiere_display()}", body_style)
        ],
        [
            Paragraph(f"<b>Thème :</b> {fiche.theme or 'Général'}", body_style),
            Paragraph(f"<b>Durée :</b> {fiche.duree_minutes} min", body_style)
        ]
    ]
    t = Table(meta_data, colWidths=[260, 260])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
    ]))
    story.append(t)
    story.append(Spacer(1, 14))

    def add_section(title, text):
        story.append(Paragraph(title, section_style))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#3B82F6"), spaceAfter=8))
        for paragraph in text.split('\n'):
            if paragraph.strip():
                story.append(Paragraph(paragraph.replace('\n', '<br/>'), body_style))
                story.append(Spacer(1, 4))
        story.append(Spacer(1, 10))

    add_section("1. Objectifs pédagogiques & Compétences", fiche.objectifs)
    add_section("2. Déroulé de la séance (5 phases)", fiche.deroule_seance)
    add_section("3. Exercices d'application & Évaluation", fiche.exercices_types)

    doc.build(story)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Fiche_{fiche.pk}.pdf"'
    return response


# ==========================================
# MODULE 2 : QCM & ÉVALUATIONS FORMATIVES
# ==========================================

@login_required
def creer_qcm_view(request):
    if request.method == 'POST':
        form = EvaluationQCMForm(request.POST)
        if form.is_valid():
            qcm = form.save(commit=False)
            qcm.enseignant = request.user

            contenu_ia = generer_contenu_qcm(
                titre=qcm.titre,
                niveau_label=qcm.get_niveau_display(),
                matiere_label=qcm.get_matiere_display(),
                notions_cles=qcm.notions_cles,
                difficulte_label=qcm.get_difficulte_display(),
                nb_questions=qcm.nb_questions
            )

            qcm.contenu_eleve = contenu_ia.get('contenu_eleve', '')
            qcm.contenu_corrige = contenu_ia.get('contenu_corrige', '')
            qcm.pistes_remediation = contenu_ia.get('pistes_remediation', '')
            qcm.save()

            messages.success(request, "QCM et corrigé générés avec succès !")
            return redirect('detail_qcm', pk=qcm.pk)
    else:
        form = EvaluationQCMForm()
    return render(request, 'preparations/creer_qcm.html', {'form': form})


@login_required
def detail_qcm_view(request, pk):
    qcm = get_object_or_404(EvaluationQCM, pk=pk, enseignant=request.user)
    return render(request, 'preparations/detail_qcm.html', {'qcm': qcm})


@login_required
def supprimer_qcm_view(request, pk):
    qcm = get_object_or_404(EvaluationQCM, pk=pk, enseignant=request.user)
    if request.method == 'POST':
        qcm.delete()
        messages.success(request, "QCM supprimé avec succès.")
        return redirect('dashboard')
    return render(request, 'preparations/supprimer_qcm.html', {'qcm': qcm})


@login_required
def exporter_pdf_qcm_view(request, pk, mode):
    """
    mode = 'eleve' (sujet seul) ou 'corrige' (sujet + corrigé + remédiation)
    """
    qcm = get_object_or_404(EvaluationQCM, pk=pk, enseignant=request.user)
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'MainTitle',
        parent=styles['Heading1'],
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#1E3A8A"),
        spaceAfter=8
    )
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#1E40AF"),
        spaceBefore=10,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#334155")
    )

    story = []
    suffixe = " - Sujet Élève" if mode == 'eleve' else " - Corrigé Enseignant"
    story.append(Paragraph(f"{qcm.titre}{suffixe}", title_style))
    story.append(Spacer(1, 4))

    if mode == 'eleve':
        meta_data = [
            [
                Paragraph(f"<b>Nom / Prénom :</b> ............................................", body_style),
                Paragraph(f"<b>Date :</b> ........................", body_style)
            ],
            [
                Paragraph(f"<b>Classe / Niveau :</b> {qcm.get_niveau_display()}", body_style),
                Paragraph(f"<b>Matière :</b> {qcm.get_matiere_display()}", body_style)
            ]
        ]
    else:
        meta_data = [
            [
                Paragraph(f"<b>Niveau :</b> {qcm.get_niveau_display()}", body_style),
                Paragraph(f"<b>Matière :</b> {qcm.get_matiere_display()}", body_style)
            ],
            [
                Paragraph(f"<b>Difficulté :</b> {qcm.get_difficulte_display()}", body_style),
                Paragraph(f"<b>Nombre de questions :</b> {qcm.nb_questions}", body_style)
            ]
        ]

    t = Table(meta_data, colWidths=[260, 260])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))

    def add_section(title, text):
        story.append(Paragraph(title, section_style))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#3B82F6"), spaceAfter=6))
        for paragraph in text.split('\n'):
            if paragraph.strip():
                story.append(Paragraph(paragraph.replace('\n', '<br/>'), body_style))
                story.append(Spacer(1, 3))
        story.append(Spacer(1, 8))

    if mode == 'eleve':
        add_section("Évaluation formative", qcm.contenu_eleve)
    else:
        add_section("1. Sujet de l'évaluation", qcm.contenu_eleve)
        add_section("2. Corrigé officiel & Barème", qcm.contenu_corrige)
        add_section("3. Pistes de remédiation & Différenciation", qcm.pistes_remediation)

    doc.build(story)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    filename = f"QCM_{qcm.pk}_{mode}.pdf"
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response