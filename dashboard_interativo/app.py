import streamlit as st
import pandas as pd
from utils import validar_cpf, validar_email
from io import BytesIO
import plotly.express as px
import re
from validate_docbr import CPF

DB_PATH = "data/banco.csv"

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
    cpf = st.text_input("CPF")
    email = st.text_input("Email")
    cargo = st.text_input("Cargo")
    setor = st.selectbox("Setor", ["Financeiro", "Tecnologia", "Vendas", "RH", "Outro"])
    salario = st.number_input("Salário", min_value=0.0, step=100.0)
    data_admissao = st.date_input("Data de Admissão")
    enviar = st.form_submit_button("Adicionar")

    if enviar:
        erros = []
        if not validar_cpf(cpf):
            erros.append("CPF inválido")
        if not validar_email(email):
            erros.append("Email inválido")
        if not nome:
            erros.append("Nome obrigatório")
        if erros:
            st.error(" | ".join(erros))
        else:
            novo = pd.DataFrame([[nome, cpf, email, cargo, setor, salario, data_admissao]], columns=df.columns)
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
        df_editado = edit_result["edited_df"] if "edited_df" in edit_result else editavel
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
    st.metric("Média Salarial", f'R$ {df["Salário"].mean():,.2f}' if not df.empty else "R$ 0,00")
with col3:
    invalidos = df["CPF"].apply(lambda x: not validar_cpf(x))
    st.metric("CPFs Inválidos", invalidos.sum())

# Gráficos Interativos
st.subheader("Gráficos Interativos")

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.markdown("Quantidade por Setor")
    if not df.empty:
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
    if not df.empty:
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
def gerar_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Dados')
    output.seek(0)
    return output

st.download_button("Baixar CSV", data=df.to_csv(index=False), file_name="dados.csv", mime="text/csv")
st.download_button("Baixar Excel", data=gerar_excel(df), file_name="dados.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
st.download_button("Baixar JSON", data=df.to_json(orient="records"), file_name="dados.json", mime="application/json")
