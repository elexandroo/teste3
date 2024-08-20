
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Função para contar lavagens
def contar_lavagens(maquinas):
    if isinstance(maquinas, str):
        return maquinas.count('Lavadora')
    else:
        return 0

# Função para contar secagens
def contar_secagens(maquinas):
    if isinstance(maquinas, str):
        return maquinas.count('Secadora')
    else:
        return 0

# Função para categorizar turnos
def categorizar_turno(hora):
    hora_int = hora.hour
    if 5 <= hora_int < 12:
        return 'Manhã'
    elif 12 <= hora_int < 18:
        return 'Tarde'
    elif 18 <= hora_int < 24:
        return 'Noite'
    else:
        return 'Madrugada'

# Título do aplicativo
st.title("Relatório de Vendas RCA")

# Upload do arquivo CSV
uploaded_file = st.file_uploader("Escolha o arquivo CSV", type="csv")

if uploaded_file is not None:
    data = pd.read_csv(uploaded_file, delimiter=';', encoding='ISO-8859-1')

    # Verificação e conversão da coluna 'Valor_Venda'
    if 'Valor_Venda' in data.columns:
        data['Valor_Venda'] = data['Valor_Venda'].str.replace('R$', '').str.replace(',', '.').str.strip()
        data['Valor_Venda'] = pd.to_numeric(data['Valor_Venda'], errors='coerce')

    # Manipulação de Data e Hora
    if 'Data_Hora' in data.columns:
        for fmt in ('%d/%m/%Y %H:%M:%S', '%d/%m/%Y %H:%M'):
            try:
                data['Data_Hora'] = pd.to_datetime(data['Data_Hora'], format=fmt)
            except ValueError:
                continue
            else:
                break
        data['Data'] = pd.to_datetime(data['Data_Hora'].dt.date, format='%Y-%m-%d')
        data['Hora'] = data['Data_Hora'].dt.time

    # Calcular métricas
    data['Turno'] = data['Hora'].apply(categorizar_turno)
    data['Quantidade_Lavagens'] = data['Maquinas'].apply(contar_lavagens)
    data['Quantidade_Secagens'] = data['Maquinas'].apply(contar_secagens)
    data['Total de Ciclos'] = data['Quantidade_Lavagens'] + data['Quantidade_Secagens']

    # Agrupar e calcular vendas por dia da semana
    data['Dia_da_Semana'] = data['Data_Hora'].dt.strftime('%A')
    vendas_por_dia = data.groupby('Dia_da_Semana')['Valor_Venda'].sum().reset_index()

    # Mostrar métricas no Streamlit
    st.subheader("Vendas por Dia da Semana")
    st.dataframe(vendas_por_dia)

    # Gráfico de vendas por dia da semana
    st.subheader("Gráfico de Vendas por Dia da Semana")
    fig, ax = plt.subplots()
    ax.bar(vendas_por_dia['Dia_da_Semana'], vendas_por_dia['Valor_Venda'])
    ax.set_ylabel('Valor Venda (R$)')
    ax.set_title('Vendas por Dia da Semana')
    st.pyplot(fig)

    # Exibir métricas adicionais
    st.subheader("Métricas Adicionais")
    st.write(f"Total de Lavagens: {data['Quantidade_Lavagens'].sum()}")
    st.write(f"Total de Secagens: {data['Quantidade_Secagens'].sum()}")
    st.write(f"Total de Ciclos: {data['Total de Ciclos'].sum()}")

    st.subheader("Resumo dos Clientes")
    st.dataframe(data[['Doc_Cliente', 'Nome_Cliente', 'Valor_Venda']].groupby(['Doc_Cliente', 'Nome_Cliente']).sum())

else:
    st.write("Por favor, faça o upload de um arquivo CSV.")
