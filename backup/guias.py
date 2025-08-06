import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import base64
from PIL import Image as PILImage

st.set_page_config(page_title="Dashboard Guias Técnicas", layout="centered")
st.title("TRABALHOS REALIZADOS NO MÊS")

# Inicializar dados e estado de edição
if "data" not in st.session_state:
    st.session_state.data = []
if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

# Inputs do cabeçalho (mês, ano, clínica)
mes = st.text_input("Mês", placeholder="Agosto", key="mes")
ano = st.text_input("Ano", placeholder="2025", key="ano")
clinica = st.text_input("Nome da Clínica", placeholder="Exemplo Clínica Dentária", key="clinica")

# Se estiver a editar, valores atuais do registo para pré-preencher formulário
if st.session_state.edit_index is not None:
    editar = st.session_state.data[st.session_state.edit_index]
    default_numero_guia = editar["Número da Guia"]
    default_nome_paciente = editar["Nome do Paciente"]
    default_medico = editar["Médico"]
    default_trabalhos = editar["Trabalhos"]
    default_valor = editar["Valor"]
else:
    default_numero_guia = ""
    default_nome_paciente = ""
    default_medico = ""
    default_trabalhos = ""
    default_valor = ""

# Formulário para adicionar/editar registo
with st.form("formulario_registo", clear_on_submit=True):
    numero_guia = st.text_input("Número da Guia", value=default_numero_guia, key="numero_guia")
    nome_paciente = st.text_input("Nome do Paciente", value=default_nome_paciente, key="nome_paciente")
    medico = st.text_input("Médico", value=default_medico, key="medico")
    trabalhos = st.text_area("Tipo(s) de Trabalho (1 por linha)", value=default_trabalhos, key="trabalhos")
    valor = st.text_area("Valor (€) (pode ser multilinha)", value=default_valor, key="valor")

    adicionar = st.form_submit_button("Adicionar/Atualizar Registo")
    cancelar = st.form_submit_button("Cancelar Edição")

    if adicionar:
        if not numero_guia.strip():
            st.warning("Preencha o Número da Guia")
        else:
            registo = {
                "Número da Guia": numero_guia.strip(),
                "Nome do Paciente": nome_paciente.strip(),
                "Médico": medico.strip(),
                "Trabalhos": trabalhos.strip(),
                "Valor": valor.strip()
            }
            if st.session_state.edit_index is not None:
                st.session_state.data[st.session_state.edit_index] = registo
                st.success("Registo atualizado com sucesso.")
                st.session_state.edit_index = None
            else:
                st.session_state.data.append(registo)
                st.success("Registo adicionado com sucesso.")

    if cancelar:
        st.session_state.edit_index = None
        st.experimental_rerun()

# Mostrar registos com botões só com ícones
if st.session_state.data:
    st.markdown("### Registos Inseridos")
    for i, row in enumerate(st.session_state.data):
        cols = st.columns([2, 3, 2, 4, 3, 0.5, 0.5])
        cols[0].write(row["Número da Guia"])
        cols[1].write(row["Nome do Paciente"])
        cols[2].write(row["Médico"])
        cols[3].write(row["Trabalhos"].replace("\n", "<br>"), unsafe_allow_html=True)
        cols[4].write(row["Valor"].replace("\n", "<br>"), unsafe_allow_html=True)

        if cols[5].button("✏️", key=f"edit_{i}", help="Editar registo"):
            st.session_state.edit_index = i
            st.experimental_rerun()

        if cols[6].button("🗑️", key=f"del_{i}", help="Apagar registo"):
            st.session_state.data.pop(i)
            st.success("Registo apagado.")
            if st.session_state.edit_index == i:
                st.session_state.edit_index = None
            st.experimental_rerun()
else:
    st.info("Sem registos ainda.")

# Função para somar valores multilinha ignorando erros
def somar_valores_multilinha(valores_multilinha):
    total = 0.0
    for val_str in valores_multilinha.split("\n"):
        val_str = val_str.strip().replace(",", ".")
        try:
            total += float(val_str)
        except:
            pass
    return total

total = 0.0
if st.session_state.data:
    for reg in st.session_state.data:
        total += somar_valores_multilinha(reg.get("Valor", ""))

st.markdown(f"### Total estimado: **{total:.2f} €**")

# Função para gerar PDF
def gerar_pdf(dados, mes, ano, clinica, total):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    styles = getSampleStyleSheet()
    elementos = []

    style_normal = styles["Normal"]
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
        fontSize=16,
        leading=18,
        spaceAfter=12
    )

    # Logo reduzido a 75%
    try:
        pil_img = PILImage.open("logo.png")
        largura_original, altura_original = pil_img.size
        largura_nova = largura_original * 0.75
        altura_nova = altura_original * 0.75
        img = Image("logo.png", width=largura_nova, height=altura_nova)
    except Exception:
        img = Paragraph("Logótipo não encontrado", style_normal)

    # Cabeçalho: logo + clínica alinhados à direita
    from reportlab.platypus import Table, TableStyle

    logo_and_clinica = [
        [img],
        [Paragraph(f"<b>{clinica}</b>", style_right)]
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
    elementos.append(Paragraph(f"Exmo. Sr.<br/>{clinica}", style_normal))
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
        trabalhos_formatado = Paragraph(row["Trabalhos"].replace("\n", "<br/>"), style_normal)
        valor_formatado = Paragraph(row["Valor"].replace("\n", "<br/>"), style_normal)
        dados_tabela.append([
            row["Número da Guia"],
            row["Nome do Paciente"],
            row["Médico"],
            trabalhos_formatado,
            valor_formatado
        ])
    dados_tabela.append(["", "", "", "Total:", f"{total:.2f} €"])

    tabela = Table(dados_tabela, colWidths=[70, 110, 90, 180, 60], hAlign='LEFT')
    tabela.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (-2, -1), (-1, -1), 'RIGHT'),
        ('FONTNAME', (-2, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elementos.append(tabela)

    doc.build(elementos)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

# Mostrar PDF embutido via base64
def mostrar_pdf_base64(pdf_bytes):
    b64 = base64.b64encode(pdf_bytes).decode()
    pdf_display = f"""
    <iframe src="data:application/pdf;base64,{b64}" width="700" height="900" type="application/pdf"></iframe>
    """
    st.markdown(pdf_display, unsafe_allow_html=True)

# Botões para pré-visualização e exportação PDF
if st.session_state.data and mes and ano and clinica:
    if st.button("Mostrar Pré-visualização PDF"):
        pdf_bytes = gerar_pdf(st.session_state.data, mes, ano, clinica, total)
        mostrar_pdf_base64(pdf_bytes)
        st.session_state.pdf_gerado = pdf_bytes

    if "pdf_gerado" in st.session_state:
        st.download_button(
            label="📄 Exportar PDF com Design",
            data=st.session_state.pdf_gerado,
            file_name="trabalhos_realizados.pdf",
            mime="application/pdf"
        )
else:
    st.info("Preencha o mês, ano, nome da clínica e adicione registos para pré-visualizar e exportar o PDF.")
