from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse
from django.contrib import messages
from django.contrib.staticfiles.finders import find
from django.db.models import Sum
from decimal import Decimal

from .models import Clinica, Guia
from .forms import ClinicaForm, GuiaForm

from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from PIL import Image as PILImage

# Funções auxiliares para PDF
def somar_valores_multilinha(valores_multilinha):
    total = Decimal('0.0')
    for val_str in valores_multilinha.split("\n"):
        val_str = val_str.strip().replace(",", ".")
        try:
            total += Decimal(val_str)
        except:
            pass
    return total

def gerar_pdf(dados, mes, ano, clinica_nome, total):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    styles = getSampleStyleSheet()
    elementos = []

    style_normal = styles["Normal"]
    style_normal.leading = 14

    style_right = ParagraphStyle(
        "right",
        parent=style_normal,
        alignment=2,
        fontSize=10,
        leading=12
    )
    style_titulo = ParagraphStyle(
        "titulo",
        parent=styles["Title"],
        alignment=1,
        fontSize=18,
        leading=22,
        spaceAfter=18
    )

    # Logo
    logo_path = find('guias_app/logo.png')
    if logo_path:
        try:
            pil_img = PILImage.open(logo_path)
            largura_original, altura_original = pil_img.size
            largura_nova = largura_original * 0.75
            altura_nova = altura_original * 0.75
            img = Image(logo_path, width=largura_nova, height=altura_nova)
        except Exception:
            img = Paragraph("Logótipo não encontrado", style_normal)
    else:
        img = Paragraph("Logótipo não encontrado", style_normal)

    # Cabeçalho: logo + clínica alinhados à direita
    from reportlab.platypus import Table, TableStyle

    logo_and_clinica = [
        [img],
        [Paragraph(f"<b>{clinica_nome}</b>", style_right)]
    ]
    tabela_logo = Table(logo_and_clinica, colWidths=[largura_nova], hAlign="RIGHT")
    tabela_logo.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (0, 0), 10),
        ('TOPPADDING', (1, 0), (1, 0), 0),
    ]))
    elementos.append(tabela_logo)
    elementos.append(Spacer(1, 20))

    # Título
    elementos.append(Paragraph(f"TRABALHOS REALIZADOS NO MÊS DE {mes.upper()} - {ano}", style_titulo))
    elementos.append(Spacer(1, 12))

    # Destinatário
    elementos.append(Paragraph(f"Exmo. Sr.<br/>{clinica_nome}", style_normal))
    elementos.append(Spacer(1, 20))

    # Informação técnica fixa
    info_tecnica = (
        "Técnica de Prótese Dentária<br/>"
        "Vânia Sofia Martins Tomé<br/>"
        "Urb. Aldeia das Amendoeiras Lote 57<br/>"
        "8200-004 Albufeira<br/>"
        "Cont. 223 229 067<br/>"
        "NIB: 0035 0018 0000 15000000 33"
    )
    elementos.append(Paragraph(info_tecnica, style_normal))
    elementos.append(Spacer(1, 25))

    # Tabela de dados
    dados_tabela = [["Número da Guia", "Nome do Paciente", "Médico", "Tipo de Trabalho", "Valor (€)"]]
    for row in dados:
        trabalhos_formatado = Paragraph(row.trabalhos.replace("\n", "<br/>"), style_normal)
        valor_formatado = Paragraph(row.valor.replace("\n", "<br/>"), style_normal)
        dados_tabela.append([
            row.numero_guia,
            row.nome_paciente,
            row.medico,
            trabalhos_formatado,
            valor_formatado
        ])
    # Total row
    dados_tabela.append(["", "", "", "<b>Total:</b>", f"<b>{total:.2f} €</b>"])

    tabela = Table(dados_tabela, colWidths=[70, 110, 90, 180, 60], hAlign='LEFT')
    tabela.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (-2, -1), (-1, -1), 'RIGHT'),
        ('FONTNAME', (-2, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('LINEBELOW', (0, -2), (-1, -2), 1, colors.black),
        ('FONTSIZE', (-2, -1), (-1, -1), 10),
    ]))
    elementos.append(tabela)

    doc.build(elementos)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

# Views para Clínicas
def clinica_list(request):
    clinicas = Clinica.objects.all().order_by('nome')
    form = ClinicaForm()
    return render(request, 'guias_app/clinica_list.html', {'clinicas': clinicas, 'form': form})

def clinica_add(request):
    if request.method == 'POST':
        form = ClinicaForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Clínica adicionada com sucesso!")
                return redirect('clinica_list')
            except Exception as e:
                if 'UNIQUE constraint failed' in str(e):
                    form.add_error('nome', "Esta clínica já existe.")
                else:
                    form.add_error(None, f"Ocorreu um erro: {e}")
    else:
        form = ClinicaForm()
    clinicas = Clinica.objects.all().order_by('nome')
    return render(request, 'guias_app/clinica_list.html', {'clinicas': clinicas, 'form': form})

def clinica_delete(request, pk):
    clinica = get_object_or_404(Clinica, pk=pk)
    clinica.delete()
    messages.success(request, "Clínica apagada com sucesso!")
    return redirect('clinica_list')

# Views para Guias
def overview_guides(request):
    # Get all closed guides
    all_closed_guias = Guia.objects.filter(is_closed=True).order_by('clinica__nome', 'ano', 'mes')

    # Group by clinic, then by month/year, and calculate totals
    grouped_data = {}
    global_total = Decimal('0.0')

    for guia in all_closed_guias:
        clinica_name = guia.clinica.nome
        month_year = f"{guia.mes}/{guia.ano}"
        guia_value = somar_valores_multilinha(guia.valor)

        if clinica_name not in grouped_data:
            grouped_data[clinica_name] = {
                'monthly_guides': {},
                'clinic_total': Decimal('0.0')
            }
        
        if month_year not in grouped_data[clinica_name]['monthly_guides']:
            grouped_data[clinica_name]['monthly_guides'][month_year] = {
                'total_value': Decimal('0.0'),
                'guia_pdf_url': reverse('guia_pdf') + f'?clinica={guia.clinica.pk}&mes={guia.mes}&ano={guia.ano}'
            }
        
        grouped_data[clinica_name]['monthly_guides'][month_year]['total_value'] += guia_value
        grouped_data[clinica_name]['clinic_total'] += guia_value
        global_total += guia_value

    clinicas = Clinica.objects.all().order_by('nome') # Still needed for navbar

    context = {
        'grouped_data': grouped_data,
        'global_total': global_total,
        'clinicas': clinicas, # For navbar
    }
    return render(request, 'guias_app/overview_guides.html', context)

def guia_close_monthly(request):
    if request.method == 'POST':
        mes = request.POST.get('mes', '')
        ano = request.POST.get('ano', '')
        clinica_id = request.POST.get('clinica', '')

        if not all([mes, ano, clinica_id]):
            messages.error(request, "Mês, Ano e Clínica são obrigatórios para encerrar a guia.")
            return redirect(reverse('guia_create') + f"?{request.POST.get('query_string', '')}")

        guias_to_close = Guia.objects.filter(mes=mes, ano=ano, clinica__id=clinica_id)

        if not guias_to_close.exists():
            messages.warning(request, "Nenhum registo encontrado para encerrar com os filtros fornecidos.")
        else:
            guias_to_close.update(is_closed=True)
            messages.success(request, f"Guia mensal para {mes}/{ano} da clínica {Clinica.objects.get(id=clinica_id).nome} encerrada com sucesso!")

        return redirect(reverse('guia_create') + f"?{request.POST.get('query_string', '')}")
    return redirect('guia_create')

def guia_create(request):
    clinica_filter_id = request.GET.get('clinica') or request.POST.get('clinica')
    mes_filter = request.GET.get('mes') or request.POST.get('mes')
    ano_filter = request.GET.get('ano') or request.POST.get('ano')

    initial_data = {}
    if clinica_filter_id:
        initial_data['clinica'] = clinica_filter_id
    if mes_filter:
        initial_data['mes'] = mes_filter
    if ano_filter:
        initial_data['ano'] = ano_filter

    if request.method == 'POST':
        form = GuiaForm(request.POST)
        if form.is_valid():
            guia = form.save()
            messages.success(request, "Registo adicionado com sucesso!")
            form = GuiaForm(initial={
                'clinica': guia.clinica.pk,
                'mes': guia.mes,
                'ano': guia.ano
            })
        else:
            pass
    else:
        form = GuiaForm(initial=initial_data)

    # Only fetch OPEN guides for the current clinic, month, and year
    guias = Guia.objects.filter(is_closed=False)
    if clinica_filter_id:
        guias = guias.filter(clinica__id=clinica_filter_id)
    if mes_filter:
        guias = guias.filter(mes__iexact=mes_filter)
    if ano_filter:
        guias = guias.filter(ano=ano_filter)

    total = sum(somar_valores_multilinha(guia.valor) for guia in guias)

    # Determine if the current filtered set of guides is closed (should be false here if we only show open guides)
    is_closed_for_filters = False # Always false for this view now
    if guias.exists(): # Check if there are any open guides for this filter
        if all(guia.is_closed for guia in guias): # This condition will likely be false now
            is_closed_for_filters = True

    clinicas = Clinica.objects.all().order_by('nome')
    clinica_nome = ""
    if clinica_filter_id:
        try:
            clinica_nome = Clinica.objects.get(id=clinica_filter_id).nome
        except Clinica.DoesNotExist:
            pass

    context = {
        'form': form,
        'clinicas': clinicas,
        'guias': guias,
        'total': total,
        'mes_filter': mes_filter,
        'ano_filter': ano_filter,
        'clinica_filter_id': clinica_filter_id,
        'is_closed_for_filters': is_closed_for_filters,
        'clinica_nome': clinica_nome,
    }
    return render(request, 'guias_app/guia_create.html', context)

def guia_delete(request, pk):
    guia = get_object_or_404(Guia, pk=pk)
    guia.delete()
    query_string = request.POST.get('query_string', '')
    return redirect(f'{reverse('guia_create')}?{query_string}')

def guia_pdf(request):
    mes_filter = request.GET.get('mes', '')
    ano_filter = request.GET.get('ano', '')
    clinica_filter_id = request.GET.get('clinica', '')

    guias = Guia.objects.all()
    if mes_filter:
        guias = guias.filter(mes__iexact=mes_filter)
    if ano_filter:
        guias = guias.filter(ano=ano_filter)
    if clinica_filter_id:
        guias = guias.filter(clinica__id=clinica_filter_id)

    clinica_nome = ""
    if clinica_filter_id:
        try:
            clinica_nome = Clinica.objects.get(id=clinica_filter_id).nome
        except Clinica.DoesNotExist:
            pass

    total = sum(somar_valores_multilinha(guia.valor) for guia in guias)

    pdf_bytes = gerar_pdf(guias, mes_filter, ano_filter, clinica_nome, total)

    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="trabalhos_realizados.pdf"'
    return response

def home(request):
    clinicas = Clinica.objects.all().order_by('nome')
    return render(request, 'guias_app/home.html', {'clinicas': clinicas})