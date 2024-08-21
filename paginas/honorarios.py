import pandas as pd
import streamlit as st
import re
from num2words import num2words

# Configurações da página inicial
st.image("images/calculadora_svg.svg", width=50)
st.title('Calculadora de Honorários Advocatícios!', anchor=False)

# Função para validar o número do processo
def validar_processo(numero):
    pattern = r'^\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}$'
    return re.match(pattern, numero) is not None

# Função para calcular o valor do Honorário
def calcular_honorario(valor_total, porcentagem):
    return valor_total * (porcentagem / 100)

# Função formatar valor com duas casas decimais e separador de milhar
def formatar_valor(valor):
    valor_formatado = f"{valor:,.2f}"
    return "R$ " + valor_formatado.replace(',', 'X').replace('.', ',').replace('X', '.')

# Converte o valor para texto por extenso em português
def valor_por_extenso(valor):
    return num2words(valor, lang='pt_BR', to='currency')

# Entrada de dados
processo = st.text_input('Insira o número do processo:', placeholder='Ex: 0123456-00.2099.8.05.0001')
autor = st.text_input('Insira o nome do autor:', placeholder='Nome do autor.')
valor_total_creditado = st.number_input('Insira o valor total creditado na conta do escritório (R$):', placeholder='R$ 0,00')
porcentagem_contratual = st.number_input('Insira a porcentagem dos honorários contratuais (%):', min_value=0)

# Checkboxes para campos opcionais
calcular_sucumbencia = st.checkbox('Incluir honorários de sucumbência?')

if calcular_sucumbencia:
    porcentagem_sucumbencia = st.number_input('Insira a porcentagem dos honorários de sucumbência (%):', min_value=0)
else:
    porcentagem_sucumbencia = 0  # Define como 0 se não for calcular

mais_advogados = st.checkbox('Dividir honorários entre advogados?')

if mais_advogados:
    quantidade_advogados=st.number_input('Insira a quantidade de advogados',min_value=2)
else:
    quantidade_advogados = 1  # Define como 1 se não houver divisão


# Botão de cálculo e lógica
if st.button('Calcular'):
    try:
        valor_formatado = formatar_valor(valor_total_creditado)
        valor_extenso = valor_por_extenso(valor_total_creditado)
        st.write(f"Valor creditado: {valor_formatado} ({valor_extenso})")
    except ValueError:
        st.error("Por favor, insira um número válido para o valor total creditado.")

    if validar_processo(processo):
        # Cálculos principais
        valor_condenacao = valor_total_creditado / (1 + porcentagem_sucumbencia / 100)
        honorarios_sucumbencia = calcular_sucumbencia and calcular_honorario(valor_condenacao, porcentagem_sucumbencia) or 0
        honorarios_contratuais = calcular_honorario(valor_condenacao, porcentagem_contratual)
        valor_para_parte = valor_condenacao - honorarios_contratuais
        valor_escritorio = honorarios_sucumbencia + honorarios_contratuais
        divisao_honorarios = valor_escritorio / quantidade_advogados

        # Criando tabela com os resultados
        dados = {
            'Descrição': [
                'Valor depositado:',
                f'Honorários de Sucumbência: ({porcentagem_sucumbencia}%.)',
                'Valor da Condenação:',
                f'Honorários Contratuais: ({porcentagem_contratual}% sobre a condenação.)',
                'Valor a ser transferido para a parte:',
                'Valor restante do escritório:',
                f'Valor para cada advogado: ({quantidade_advogados})'
            ],
            'Valor': [
                formatar_valor(valor_total_creditado),
                formatar_valor(honorarios_sucumbencia),
                formatar_valor(valor_condenacao),
                formatar_valor(honorarios_contratuais),
                formatar_valor(valor_para_parte),
                formatar_valor(valor_escritorio),
                formatar_valor(divisao_honorarios)
            ]
        }

        st.divider()

        st.write(f'Processo nº: {processo}')
        st.write(f'Autor: **{autor}**')
        tabela = pd.DataFrame(dados)
        st.table(tabela)

        # Criação de CSV e botão de download
        header_string = f"Processo nº: {processo}.\nAutor: {autor}.\n"
        csv_data = tabela.to_csv(index=False)
        full_csv = header_string + csv_data
        csv_bytes = ('\ufeff' + full_csv).encode('utf-8')
        st.download_button(label='Baixar tabela', data=csv_bytes, file_name='tabela.csv', mime='text/csv')

        st.divider()
    else:
        st.error("Formato inválido! Por favor, insira o número no formato 0123456-00.2099.8.05.0001.")

