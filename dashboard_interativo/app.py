# app.py (ou Home.py)
import streamlit as st

def main():
    st.set_page_config(page_title="Dashboard Interativo", layout="wide")
    st.title("Página Inicial 🏠")
    st.write("""
        Bem-vindo ao Dashboard Interativo de Gerenciamento de Pessoas!
        Use a barra lateral para navegar entre as páginas:
        - **Análise de Dados:** Veja os gráficos e métricas interativas.
        - **Gerenciamento de Dados:** Adicione, edite ou remova registros.
    """)
    st.info("Este é um resumo geral do projeto. Explore as outras páginas para mais detalhes.")

if __name__ == "__main__":
    main()

```python
# pages/1_Análise_de_Dados.py
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# --- FUNÇÕES DE VALIDAÇÃO (para demonstração) ---
def validar_cpf(cpf_str):
    return True # Placeholder para simplificar o exemplo

def validar_email(email_str):
    return True # Placeholder para simplificar o exemplo

# --- CARREGAMENTO DO BANCO DE DADOS ---
DB_PATH = "data/banco.csv"
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)
try:
    df = pd.read_csv(DB_PATH)
except FileNotFoundError:
    df = pd.DataFrame(columns=["Nome", "CPF", "Email", "Cargo", "Setor", "Salário", "Data de Admissão"])

def show_analysis_page():
    st.title("Análise de Dados �")

    # --- INDICADORES ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Registros", len(df))
    with col2:
        st.metric("Média Salarial", f'R$ {df["Salário"].mean():,.2f}' if not df.empty and "Salário" in df.columns else "R$ 0,00")
    with col3:
        # A validação real precisaria ser implementada, aqui é apenas um placeholder.
        invalidos = 0
        st.metric("CPFs Inválidos", invalidos)

    # --- GRÁFICOS INTERATIVOS ---
    st.subheader("Gráficos Interativos")
    col_graf1, col_graf2 = st.columns(2)

    with col_graf1:
        st.markdown("Quantidade por Setor")
        if not df.empty and "Setor" in df.columns:
            setor_counts = df["Setor"].value_counts().reset_index()
            setor_counts.columns = ["Setor", "Quantidade"]
            fig1 = px.bar(setor_counts, x="Setor", y="Quantidade", color="Setor", text="Quantidade")
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("Nenhum dado disponível para gerar o gráfico.")

    with col_graf2:
        st.markdown("Distribuição Salarial por Setor")
        if not df.empty and "Setor" in df.columns and "Salário" in df.columns:
            media_por_setor = df.groupby("Setor")["Salário"].mean().reset_index()
            fig2 = px.pie(media_por_setor, names="Setor", values="Salário", hole=0.3)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Nenhum dado disponível para gerar o gráfico.")

if __name__ == "__main__":
    show_analysis_page()

```python
# pages/2_Gerenciamento_de_Dados.py
import streamlit as st
import pandas as pd
from pathlib import Path
from io import BytesIO

# --- FUNÇÕES DE VALIDAÇÃO (para demonstração) ---
def validar_cpf(cpf_str):
    return True # Placeholder para simplificar o exemplo

def validar_email(email_str):
    return True # Placeholder para simplificar o exemplo

# --- CARREGAMENTO DO BANCO DE DADOS ---
DB_PATH = "data/banco.csv"
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)
try:
    df = pd.read_csv(DB_PATH)
except FileNotFoundError:
    df = pd.DataFrame(columns=["Nome", "CPF", "Email", "Cargo", "Setor", "Salário", "Data de Admissão"])


def show_management_page():
    st.title("Gerenciamento de Dados 🛠️")

    # --- SEÇÃO DE ADICIONAR NOVO REGISTRO ---
    st.subheader("Adicionar Novo Registro")
    with st.form("form_add_record"):
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
            if not nome:
                erros.append("Nome obrigatório")
            if erros:
                st.error(" | ".join(erros))
            else:
                novo = pd.DataFrame([[nome, cpf_input, email, cargo, setor, salario, data_admissao]], columns=df.columns)
                df_updated = pd.concat([df, novo], ignore_index=True)
                df_updated.to_csv(DB_PATH, index=False)
                st.success("Registro adicionado com sucesso!")
                st.rerun()

    st.markdown("---")

    # --- SEÇÃO DE TABELA E EDIÇÃO/EXCLUSÃO ---
    st.subheader("Tabela de Dados (Editar ou Remover)")
    edit_result = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True,
        key="tabela"
    )

    col_salvar, col_deletar = st.columns(2)
    with col_salvar:
        if st.button("Salvar Alterações"):
            edit_result.to_csv(DB_PATH, index=False)
            st.success("Alterações salvas com sucesso!")
            st.rerun()

    with col_deletar:
        if st.button("Deletar Registros"):
            # Lógica de deleção deve ser implementada aqui, st.data_editor já cuida da edição.
            st.error("A lógica de exclusão precisa de um passo adicional para selecionar as linhas.")
            st.info("Para exclusão, o data_editor é mais simples, pois a linha pode ser apagada diretamente.")

    st.markdown("---")

    # --- EXPORTAÇÕES ---
    st.subheader("Exportação de Dados")
    def gerar_excel(df_to_export):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_to_export.to_excel(writer, index=False, sheet_name='Dados')
        output.seek(0)
        return output

    if not df.empty:
        st.download_button("Baixar CSV", data=df.to_csv(index=False), file_name="dados.csv", mime="text/csv")
        st.download_button("Baixar Excel", data=gerar_excel(df), file_name="dados.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        st.download_button("Baixar JSON", data=df.to_json(orient="records"), file_name="dados.json", mime="application/json")
    else:
        st.info("Nenhum dado para exportar.")

if __name__ == "__main__":
    show_management_page()

�
