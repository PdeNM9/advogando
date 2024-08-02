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
porcentagem_sucumbencia = st.number_input('Insira a porcentagem dos honorários de sucumbência (%):', min_value=0)
porcentagem_contratual = st.number_input('Insira a porcentagem dos honorários contratuais (%):', min_value=0)
quantidade_advogados = st.number_input('Insira a quantidade de advogados', min_value=1)

# Botão de cálculo e lógica
if st.button('Calcular'):
    try:
      valor_formatado = formatar_valor(valor_total_creditado)
      valor_extenso = valor_por_extenso(valor_total_creditado)
      st.write(f"Valor creditado: {valor_formatado} ({valor_extenso})")
    except ValueError:
        st.error("Por favor, insira um número válido para o valor total creditado.")

    if validar_processo(processo):
        # Restante do código de cálculo, assumindo que o valor total e o número do processo são válidos.
        pass
    else:
        st.error("Formato inválido! Por favor, insira o número no formato 0123456-00.2099.8.05.0001.")


    # Calculando a sucumbência sobre a condenação.
    valor_condenacao = valor_total_creditado / (1 + porcentagem_sucumbencia / 100)

    # Calculando o valor dos honorários de sucumbência
    honorarios_sucumbencia = calcular_honorario(valor_condenacao,
                                                porcentagem_sucumbencia)

    # Calculando honorários contratuais sobre a condenação
    honorarios_contratuais = calcular_honorario(valor_condenacao,
                                                porcentagem_contratual)

    # Calculando o valor a ser transferido para a parte
    valor_para_parte = valor_condenacao - honorarios_contratuais

    # Valor que restará ao escritório
    valor_escritorio = honorarios_sucumbencia + honorarios_contratuais

    # Dividindo o total de honorários pela quantidade de advogados
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

    # Cria a string de cabeçalho personalizada com as variáveis globais     

    header_string = f"Processo nº: {processo}.\nAutor: {autor}.\n"

    # Converte DataFrame para CSV     

    csv_data = tabela.to_csv(index=False)

    # Concatena o cabeçalho personalizado com os dados do CSV     

    full_csv = header_string + csv_data

    # Converte para bytes incluindo o BOM     

    csv_bytes = ('\ufeff' + full_csv).encode('utf-8')

    # Botão para baixar a tabela como CSV     

    st.download_button(label='Baixar tabela', data=csv_bytes, file_name='tabela.csv', mime='text/csv')

    st.divider()
