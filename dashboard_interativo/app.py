
import streamlit as st
import pandas as pd
import plotly.express as px
from utils import validar_cpf, validar_cnpj, validar_email

st.set_page_config(page_title="Dashboard Interativo", layout="wide")

# ---- LEITURA DA BASE ----
df = pd.read_csv("data/base_clientes.csv")

st.title("📊 Dashboard Interativo com Python")

# ---- FILTRO E DADOS ----
setores = df['setor'].unique().tolist()
setor_select = st.sidebar.multiselect("Filtrar por setor", setores, default=setores)

df_filtrado = df[df["setor"].isin(setor_select)]

# ---- GRÁFICO SALÁRIOS ----
fig_salario = px.box(df_filtrado, x="setor", y="salario", title="Distribuição Salarial por Setor")
st.plotly_chart(fig_salario, use_container_width=True)

# ---- MÉTRICAS ----
col1, col2, col3 = st.columns(3)
col1.metric("Total de Funcionários", len(df_filtrado))
col2.metric("Média Salarial", f"R$ {df_filtrado['salario'].mean():,.2f}")
col3.metric("CPFs Inválidos", df_filtrado['cpf'].apply(lambda x: not validar_cpf(str(x)) if pd.notna(x) else False).sum())

# ---- TABELA ----
st.subheader("📄 Tabela de Dados")
st.dataframe(df_filtrado, use_container_width=True)

# ---- EXPORTAR ----
st.download_button("📥 Exportar CSV", df_filtrado.to_csv(index=False), "dados.csv", "text/csv")
from io import BytesIO

def gerar_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Dados')
    output.seek(0)
    return output

excel_bytes = gerar_excel(df_filtrado)
st.download_button(
    label="📥 Exportar Excel",
    data=excel_bytes,
    file_name="dados.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.download_button("📥 Exportar JSON", df_filtrado.to_json(orient="records"), "dados.json", "application/json")

# ---- FORMULÁRIO PARA INSERÇÃO ----
st.subheader("➕ Inserir Novo Registro")
with st.form("form_novo_dado"):
    nome = st.text_input("Nome")
    cpf = st.text_input("CPF (somente números)")
    email = st.text_input("Email")
    setor = st.selectbox("Setor", ["Financeiro", "Tecnologia", "Vendas", "Recursos Humanos"])
    salario = st.number_input("Salário", min_value=0.0, step=100.0)
    status = st.selectbox("Status", ["Ativo", "Inativo"])
    enviado = st.form_submit_button("Salvar")

    if enviado:
        novo = {
            "id": df["id"].max() + 1,
            "nome": nome,
            "cpf": cpf,
            "cnpj": "",
            "email": email,
            "data_nascimento": "2000-01-01",  # provisório
            "setor": setor,
            "salario": salario,
            "data_registro": pd.Timestamp.today().strftime("%Y-%m-%d"),
            "status": status
        }
        df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
        df.to_csv("data/base_clientes.csv", index=False)
        st.success("Registro salvo com sucesso!")
