from django import forms
from .models import Clinica, Guia

class ClinicaForm(forms.ModelForm):
    class Meta:
        model = Clinica
        fields = ['nome']

class GuiaForm(forms.ModelForm):
    MES_CHOICES = [
        ('Janeiro', 'Janeiro'), ('Fevereiro', 'Fevereiro'), ('Março', 'Março'),
        ('Abril', 'Abril'), ('Maio', 'Maio'), ('Junho', 'Junho'),
        ('Julho', 'Julho'), ('Agosto', 'Agosto'), ('Setembro', 'Setembro'),
        ('Outubro', 'Outubro'), ('Novembro', 'Novembro'), ('Dezembro', 'Dezembro'),
    ]
    ANO_CHOICES = [
        ('2025', '2025'), ('2026', '2026'), ('2027', '2027'),
    ]

    mes = forms.ChoiceField(choices=MES_CHOICES, label="Mês")
    ano = forms.ChoiceField(choices=ANO_CHOICES, label="Ano")

    class Meta:
        model = Guia
        fields = ['clinica', 'numero_guia', 'nome_paciente', 'medico', 'trabalhos', 'valor', 'mes', 'ano']
        widgets = {
            'valor': forms.Textarea(attrs={'rows': 4}), # Make valor a textarea
        }