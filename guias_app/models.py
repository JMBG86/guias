from django.db import models

class Clinica(models.Model):
    nome = models.CharField(max_length=255, unique=True, verbose_name="Nome da Clínica")

    class Meta:
        verbose_name = "Clínica"
        verbose_name_plural = "Clínicas"

    def __str__(self):
        return self.nome

class Guia(models.Model):
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE, verbose_name="Clínica")
    numero_guia = models.CharField(max_length=255, verbose_name="Número da Guia")
    nome_paciente = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nome do Paciente")
    medico = models.CharField(max_length=255, blank=True, null=True, verbose_name="Médico")
    trabalhos = models.TextField(blank=True, null=True, verbose_name="Tipo(s) de Trabalho")
    valor = models.CharField(max_length=255, blank=True, null=True, verbose_name="Valor (€)") # Keeping as CharField to match original, consider DecimalField for calculations
    mes = models.CharField(max_length=50, verbose_name="Mês")
    ano = models.CharField(max_length=4, verbose_name="Ano")
    is_closed = models.BooleanField(default=False, verbose_name="Encerrada")

    class Meta:
        verbose_name = "Guia"
        verbose_name_plural = "Guias"
        unique_together = ('numero_guia', 'clinica', 'mes', 'ano') # Prevent duplicate entries for the same guide in the same clinic/month/year

    def __str__(self):
        return f"Guia {self.numero_guia} - {self.nome_paciente} ({self.clinica.nome})"