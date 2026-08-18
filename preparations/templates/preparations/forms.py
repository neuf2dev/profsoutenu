from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import FichePreparation


class InscriptionForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-2.5 bg-slate-50 border border-slate-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:outline-none text-slate-800 text-sm'
            })


class FichePreparationForm(forms.ModelForm):
    class Meta:
        model = FichePreparation
        fields = ['titre', 'niveau', 'matiere', 'duree_minutes', 'theme']
        widgets = {
            'titre': forms.TextInput(attrs={'placeholder': 'Ex : Découvrir les fractions simples', 'class': 'w-full px-4 py-2 border rounded-xl'}),
            'theme': forms.TextInput(attrs={'placeholder': 'Ex : Partage équitable, manipulation...', 'class': 'w-full px-4 py-2 border rounded-xl'}),
        }


class FicheEditionForm(forms.ModelForm):
    class Meta:
        model = FichePreparation
        fields = ['titre', 'theme', 'objectifs', 'deroule_seance', 'exercices_types']
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 bg-slate-50 border border-slate-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:outline-none text-slate-800 font-semibold'
            }),
            'theme': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 bg-slate-50 border border-slate-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:outline-none text-slate-800'
            }),
            'objectifs': forms.Textarea(attrs={
                'rows': 5,
                'class': 'w-full p-4 bg-slate-50 border border-slate-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:outline-none text-slate-700 text-sm font-mono leading-relaxed'
            }),
            'deroule_seance': forms.Textarea(attrs={
                'rows': 12,
                'class': 'w-full p-4 bg-slate-50 border border-slate-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:outline-none text-slate-700 text-sm font-mono leading-relaxed'
            }),
            'exercices_types': forms.Textarea(attrs={
                'rows': 8,
                'class': 'w-full p-4 bg-slate-50 border border-slate-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:outline-none text-slate-700 text-sm font-mono leading-relaxed'
            }),
        }