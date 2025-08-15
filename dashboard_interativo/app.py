# app.py
import streamlit as st
import pandas as pd
from io import BytesIO
import plotly.express as px
from pathlib import Path
import re
from validate_docbr import CPF

# --- FUNÇÕES DE VALIDAÇÃO ---
def validar_cpf(cpf_str):
    """
    Valida um CPF removendo caracteres não numéricos.
    Recebe: string com o CPF.
    Retorna: True se o CPF for válido, False caso contrário.
    """
    if not isinstance(cpf_str, str) or not cpf_str.strip():
        return False
    # Remove todos os caracteres que não são dígitos
    cpf_limpo = re.sub(r'\D', '', cpf_str)
    cpf_validator = CPF()
    return cpf_validator.validate(cpf_limpo)

def validar_email(email_str):
    """
    Valida um email usando uma expressão regular.
    Recebe: string com o email.
    Retorna: True se o email for válido, False caso contrário.
    """
    if not isinstance(email_str, str) or not email_str.strip():
        return False
    return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email_str) is not None

# --- CONFIGURAÇÃO DA PÁGINA ---
DB_PATH = "data/banco.csv"

# --- VERIFICAR E CRIAR O DIRETÓRIO DE DADOS ---
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

st.set_page_config(page_title="Dashboard Interativo ", layout="wide")
st.title("Dashboard Interativo (pessoas)")

# Inicializa a base de dados
try:
    df = pd.read_csv(DB_PATH)
except FileNotFoundError:
    df = pd.DataFrame(columns=["Nome", "CPF", "Email", "Cargo", "Setor", "Salário", "Data de Admissão"])
    df.to_csv(DB_PATH, index=False)

# Sidebar – Adicionar novo registro
st.sidebar.header("Adicionar Novo Registro")
with st.sidebar.form("formulario"):
    nome = st.text_input("Nome")
    cpf_input = st.text_input("CPF")
    email = st.text_input("Email")
    cargo = st.text_input("Cargo")
    setor = st.selectbox("Setor", ["Financeiro", "Tecnologia", "Vendas", "RH", "Outro"])
    salario = st.number_input("Salário", min_value=0.0, step=100.0)
    data_admissao = st.date_input("Data de Admissão")
    enviar = st.form_submit_button("Adicionar")

    if enviar:
        erros = []
        if not validar_cpf(str(cpf_input)):
            erros.append("CPF inválido")
        if not validar_email(email):
            erros.append("Email inválido")
        if not nome:
            erros.append("Nome obrigatório")
        if erros:
            st.error(" | ".join(erros))
        else:
            novo = pd.DataFrame([[nome, cpf_input, email, cargo, setor, salario, data_admissao]], columns=df.columns)
            df = pd.concat([df, novo], ignore_index=True)
            df.to_csv(DB_PATH, index=False)
            st.success("Registro adicionado com sucesso!")
            st.rerun()

# Mostra os dados
st.subheader("Tabela de Dados (Editar ou Remover)")
editavel = df.copy()
edit_result = st.data_editor(
    editavel,
    num_rows="dynamic",
    use_container_width=True,
    key="tabela"
)

# Botões de salvar e deletar
col_salvar, col_deletar = st.columns(2)

with col_salvar:
    if st.button("Salvar alterações"):
        df_editado = edit_result
        df_editado.to_csv(DB_PATH, index=False)
        st.success("Alterações salvas com sucesso!")
        st.rerun()

with col_deletar:
    st.warning("Para deletar, selecione uma ou mais linhas e clique abaixo.")
    rows_to_delete = st.multiselect(
        "Selecione linhas para remover:",
        df.index,
        format_func=lambda x: f"{df.iloc[x]['Nome']} - {df.iloc[x]['CPF']}"
    )
    if st.button("Deletar selecionados"):
        df = df.drop(rows_to_delete)
        df.to_csv(DB_PATH, index=False)
        st.success("Registros removidos com sucesso!")
        st.rerun()

# Indicadores
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total de Registros", len(df))
with col2:
    st.metric("Média Salarial", f'R$ {df["Salário"].mean():,.2f}' if not df.empty and "Salário" in df.columns else "R$ 0,00")
with col3:
    invalidos = df["CPF"].apply(lambda x: not validar_cpf(str(x)) if pd.notna(x) else False)
    st.metric("CPFs Inválidos", invalidos.sum())

# Gráficos Interativos
st.subheader("Gráficos Interativos")

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.markdown("Quantidade por Setor")
    if not df.empty and "Setor" in df.columns:
        setor_counts = df["Setor"].value_counts().reset_index()
        setor_counts.columns = ["Setor", "Quantidade"]
        fig1 = px.bar(
            setor_counts,
            x="Setor",
            y="Quantidade",
            color="Setor",
            text="Quantidade",
            hover_data={"Setor": True, "Quantidade": True}
        )
        fig1.update_traces(textposition="outside")
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("Nenhum dado disponível para gerar o gráfico.")

with col_graf2:
    st.markdown("Distribuição Salarial por Setor")
    if not df.empty and "Setor" in df.columns and "Salário" in df.columns:
        media_por_setor = df.groupby("Setor")["Salário"].mean().reset_index()
        fig2 = px.pie(
            media_por_setor,
            names="Setor",
            values="Salário",
            hole=0.3
        )
        fig2.update_traces(hovertemplate="Setor: %{label}<br>Salário médio: R$ %{value:,.2f}")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Nenhum dado disponível para gerar o gráfico.")

# Exportações
def gerar_excel(df_to_export):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_to_export.to_excel(writer, index=False, sheet_name='Dados')
    output.seek(0)
    return output

st.subheader("Exportação de Dados")
if not df.empty:
    st.download_button("Baixar CSV", data=df.to_csv(index=False), file_name="dados.csv", mime="text/csv")
    st.download_button("Baixar Excel", data=gerar_excel(df), file_name="dados.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.download_button("Baixar JSON", data=df.to_json(orient="records"), file_name="dados.json", mime="application/json")
else:
    st.info("Nenhum dado para exportar.")

# --- NOVA SEÇÃO: Envio Agendado por Email ---
st.markdown("---")
st.header("📧 Envio Agendado por Email")

if 'email_prefs' not in st.session_state:
    st.session_state.email_prefs = {
        "email": "",
        "frequencia": "Diário",
        "formatos": []
    }

with st.expander("Configurar Agendamento de Email"):
    with st.form("form_email_agendado"):
        email_destino = st.text_input("Seu Email", value=st.session_state.email_prefs["email"])
        frequencia = st.selectbox("Frequência de Envio", ["Diário", "Semanal", "Mensal"], index=["Diário", "Semanal", "Mensal"].index(st.session_state.email_prefs["frequencia"]))
        formatos = st.multiselect("Formatos dos Arquivos", ["CSV", "XLSX", "JSON"], default=st.session_state.email_prefs["formatos"])
        enviar_agendamento = st.form_submit_button("Salvar Preferências")

        if enviar_agendamento:
            erros_email = []
            if not validar_email(email_destino):
                erros_email.append("Email inválido")
            if not formatos:
                erros_email.append("Selecione pelo menos um formato de arquivo")

            if erros_email:
                st.error(" | ".join(erros_email))
            else:
                st.session_state.email_prefs["email"] = email_destino
                st.session_state.email_prefs["frequencia"] = frequencia
                st.session_state.email_prefs["formatos"] = formatos
                st.success(f"Preferências de envio salvas! Você receberá os dados em '{email_destino}' com frequência '{frequencia}' nos formatos: {', '.join(formatos)}.")

