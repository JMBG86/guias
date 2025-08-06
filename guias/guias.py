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
import sqlite3

# Funções da Base de Dados
def init_db():
    conn = sqlite3.connect('guias.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS clinicas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS guias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_guia TEXT NOT NULL,
            nome_paciente TEXT,
            medico TEXT,
            trabalhos TEXT,
            valor TEXT,
            mes TEXT NOT NULL,
            ano TEXT NOT NULL,
            clinica_id INTEGER,
            FOREIGN KEY (clinica_id) REFERENCES clinicas (id)
        )
    ''')
    conn.commit()
    conn.close()

def get_clinicas():
    conn = sqlite3.connect('guias.db')
    c = conn.cursor()
    c.execute("SELECT nome FROM clinicas ORDER BY nome")
    clinicas = [row[0] for row in c.fetchall()]
    conn.close()
    return clinicas

def get_clinica_id(nome_clinica):
    conn = sqlite3.connect('guias.db')
    c = conn.cursor()
    c.execute("SELECT id FROM clinicas WHERE nome = ?", (nome_clinica,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def add_clinica(nome):
    conn = sqlite3.connect('guias.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO clinicas (nome) VALUES (?)", (nome,))
        conn.commit()
        st.success(f"Clínica '{nome}' adicionada com sucesso!")
    except sqlite3.IntegrityError:
        st.error(f"A clínica '{nome}' já existe.")
    finally:
        conn.close()

def delete_clinica(nome):
    conn = sqlite3.connect('guias.db')
    c = conn.cursor()
    c.execute("DELETE FROM clinicas WHERE nome = ?", (nome,))
    conn.commit()
    conn.close()
    st.success(f"Clínica '{nome}' apagada com sucesso!")

def get_guias(clinica_id, mes, ano):
    conn = sqlite3.connect('guias.db')
    c = conn.cursor()
    c.execute("SELECT id, numero_guia, nome_paciente, medico, trabalhos, valor FROM guias WHERE clinica_id = ? AND mes = ? AND ano = ?", (clinica_id, mes, ano))
    guias = c.fetchall()
    conn.close()
    return guias

def add_guia(numero_guia, nome_paciente, medico, trabalhos, valor, mes, ano, clinica_id):
    conn = sqlite3.connect('guias.db')
    c = conn.cursor()
    c.execute("INSERT INTO guias (numero_guia, nome_paciente, medico, trabalhos, valor, mes, ano, clinica_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (numero_guia, nome_paciente, medico, trabalhos, valor, mes, ano, clinica_id))
    conn.commit()
    conn.close()

def update_guia(guia_id, numero_guia, nome_paciente, medico, trabalhos, valor):
    conn = sqlite3.connect('guias.db')
    c = conn.cursor()
    c.execute("UPDATE guias SET numero_guia = ?, nome_paciente = ?, medico = ?, trabalhos = ?, valor = ? WHERE id = ?", (numero_guia, nome_paciente, medico, trabalhos, valor, guia_id))
    conn.commit()
    conn.close()

def delete_guia(guia_id):
    conn = sqlite3.connect('guias.db')
    c = conn.cursor()
    c.execute("DELETE FROM guias WHERE id = ?", (guia_id,))
    conn.commit()
    conn.close()

# Inicializar a base de dados
init_db()

# --- PÁGINA DE GESTÃO DE CLÍNICAS ---
def page_gestao_clinicas():
    st.title("Gestão de Clínicas")

    st.subheader("Adicionar Nova Clínica")
    with st.form("form_add_clinica", clear_on_submit=True):
        novo_nome_clinica = st.text_input("Nome da nova clínica")
        submitted = st.form_submit_button("Adicionar Clínica")
        if submitted and novo_nome_clinica:
            add_clinica(novo_nome_clinica)

    st.subheader("Clínicas Existentes")
    clinicas = get_clinicas()
    if not clinicas:
        st.info("Nenhuma clínica registada.")
    else:
        for clinica in clinicas:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(clinica)
            with col2:
                if st.button("Apagar", key=f"del_{clinica}"):
                    delete_clinica(clinica)
                    st.experimental_rerun()

# --- PÁGINA PRINCIPAL ---
def page_principal():
    st.title("TRABALHOS REALIZADOS NO MÊS")

    st.title("TRABALHOS REALIZADOS NO MÊS")

    mes = st.text_input("Mês", placeholder="Agosto", key="mes")
    ano = st.text_input("Ano", placeholder="2025", key="ano")

    clinicas = get_clinicas()
    if not clinicas:
        st.warning("Não há clínicas registadas. Adicione uma na página 'Gestão de Clínicas'.")
        return

    clinica_selecionada = st.selectbox("Selecione a Clínica", clinicas)
    clinica_id = get_clinica_id(clinica_selecionada)

    # Validate mes, ano, and clinica_id before proceeding
    if not mes.strip() or not ano.strip() or clinica_id is None:
        st.warning("Por favor, preencha o Mês, o Ano e selecione uma Clínica para continuar.")
        return

    with st.form("formulario_registo", clear_on_submit=True):
        numero_guia = st.text_input("Número da Guia")
        nome_paciente = st.text_input("Nome do Paciente")
        medico = st.text_input("Médico")
        trabalhos = st.text_area("Tipo(s) de Trabalho (1 por linha)")
        valor = st.text_area("Valor (€) (pode ser multilinha)")

        adicionar = st.form_submit_button("Adicionar Registo")

        if adicionar:
            if not numero_guia.strip():
                st.warning("Por favor, preencha o campo 'Número da Guia'.")
            else:
                add_guia(numero_guia, nome_paciente, medico, trabalhos, valor, mes, ano, clinica_id)
                st.success("Registo adicionado com sucesso.")
                st.experimental_rerun()

    guias = get_guias(clinica_id, mes, ano)
    if guias:
        st.markdown("### Registos Inseridos")
        for guia in guias:
            guia_id, numero_guia, nome_paciente, medico, trabalhos, valor = guia
            cols = st.columns([2, 3, 2, 4, 3, 0.5]) # Removed edit button column
            cols[0].write(numero_guia)
            cols[1].write(nome_paciente)
            cols[2].write(medico)
            cols[3].write(trabalhos.replace("\n", "<br>"), unsafe_allow_html=True)
            cols[4].write(valor.replace("\n", "<br>"), unsafe_allow_html=True)

            if cols[5].button("🗑️", key=f"del_{guia_id}", help="Apagar registo"):
                    delete_guia(guia_id)
                    st.success("Registo apagado.")
                    st.experimental_rerun()
    else:
        st.info("Sem registos para este mês/ano/clínica.")

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
    guias_for_total = get_guias(clinica_id, mes, ano) # Re-fetch guias for total calculation
    for guia in guias_for_total:
        total += somar_valores_multilinha(guia[5])

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
            trabalhos_formatado = Paragraph(row[4].replace("\n", "<br/>"), style_normal)
            valor_formatado = Paragraph(row[5].replace("\n", "<br/>"), style_normal)
            dados_tabela.append([
                row[1],
                row[2],
                row[3],
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
        pdf_display = f'''
        <iframe src="data:application/pdf;base64,{b64}" width="700" height="900" type="application/pdf"></iframe>
        '''
        st.markdown(pdf_display, unsafe_allow_html=True)

    # Botões para pré-visualização e exportação PDF
    if guias: # Use the guias fetched earlier
        if st.button("Mostrar Pré-visualização PDF"):
                pdf_bytes = gerar_pdf(guias, mes, ano, clinica_selecionada, total)
                mostrar_pdf_base64(pdf_bytes)
        st.download_button(
            label="📄 Exportar PDF com Design",
            data=gerar_pdf(guias, mes, ano, clinica_selecionada, total), # Regenerate PDF for download
            file_name="trabalhos_realizados.pdf",
            mime="application/pdf"
        )

# --- NAVEGAÇÃO ---
st.sidebar.title("Navegação")
page = st.sidebar.radio("Escolha uma página", ["Registo de Guias", "Gestão de Clínicas"])

if page == "Registo de Guias":
    page_principal()
elif page == "Gestão de Clínicas":
    page_gestao_clinicas()