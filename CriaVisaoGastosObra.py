
# Importando pacotes.
import pandas as pd 
import matplotlib.pyplot as plt
import plotly.express as px
import streamlit as st 

st.set_page_config( layout = 'wide' ) # configura visualização para expandir na página.

# Função para formatar os números de uma visualização.
def formata_numero( valor, prefixo = '' ) :
    for unidade in [ '', 'mil' ]:
        if valor < 1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} milhões'

# Título do Dash.
st.title( 'DASHBOARD DA REFORMA :house_buildings:' )

# Criando sidebar de filtro.
st.sidebar.title( 'Filtros' ) # adiciona barra de navegação à esquerda com o título de 'Filtros'.

# Leitura da planilha
dados = pd.read_excel( 'Planilha.xlsx', sheet_name = 'Pagamentos' )

# Os 12 meses do ano para serem buscados.
vetorMesesBusca = [ 'JANEIRO', 'FEVEREIRO', 'MARÇO', 'ABRIL', 'MAIO', 'JUNHO', 'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO' ]

# Index das aparições de meses.
listaIndex = list( dados[ ( dados[ 'Unnamed: 0' ].str.contains( '|'.join( vetorMesesBusca ), na = False ) ) ][ 'Unnamed: 0' ].index )

# Meses que aparecem.
vetorMeses = list( dados[ ( dados[ 'Unnamed: 0' ].str.contains( '|'.join( vetorMesesBusca ), na = False ) ) ][ 'Unnamed: 0' ] )

# Tupla dos indexes e meses que aparecem.
tuplaMeses = ( listaIndex, vetorMeses )

# Dataframe de pagamentos.
pagamentos = dados[ ( ~dados[ 'Unnamed: 1' ].isna() ) ]

# Variáveis do banco de dados de pagamentos.
varPagamentos = list( pagamentos.iloc[ 0, : ] )

# Retirando primeira linha e atribuindo cabeçário.
pagamentos = pagamentos.iloc[ 1:, : ]

# Cabeçário.
pagamentos.columns = varPagamentos

# Criando variável vazia de mês e ano.
pagamentos = pagamentos.assign( MES_ANO = '' )

# Iteração para rotular o mês.
for j in list( pagamentos.index ):
    for i in range( len( tuplaMeses[ 1 ] ) - 1 ): 
        if ( j > tuplaMeses[ 0 ][ i ] ) & ( j < tuplaMeses[ 0 ][ i + 1 ] ):
            pagamentos.loc[ j, 'MES_ANO' ] = tuplaMeses[ 1 ][ i ]
            continue
        elif ( j > tuplaMeses[ 0 ][ i + 1 ] ):
            pagamentos.loc[ j, 'MES_ANO' ] = tuplaMeses[ 1 ][ len( tuplaMeses[ 1 ] ) - 1 ]

# Retirando dados de cabeçário que se repete.
pagamentos = pagamentos[ pagamentos[ pagamentos.columns[ 0 ] ] != pagamentos.columns[ 0 ] ]

# Filtrando colunas de interesse.
pagamentos = pagamentos[ [ 'SERVIÇO', 'FORNECEDOR', 'MES_ANO', 'VALOR' ] ]

# Pegando indexes que ficaram com notação de reais.
indexadoresAux = pagamentos[ pagamentos[ 'VALOR' ].str.contains( ',', na = False, regex = True ) ].index

# Fazendo o ajuste: tira o símbolo de dinheiro, tira o ponto de milhar, troca a vírgula por ponto.
pagamentos.loc[ indexadoresAux, 'VALOR' ] = pagamentos.loc[ indexadoresAux, 'VALOR' ].apply( lambda x: x.replace( 'R$', '' ).replace( '.', '' ).replace( ',', '.' ) )

# Transformando em float.
pagamentos[ 'VALOR' ] = pagamentos[ 'VALOR' ].astype( float )

# Criando visão de Mês e Ano.
pagamentos[ 'MES' ] = pagamentos[ 'MES_ANO' ].apply( lambda x: x.split( '-' )[ 0 ].strip() )
pagamentos[ 'ANO' ] = pagamentos[ 'MES_ANO' ].apply( lambda x: x.split( '-' )[ 1 ].strip() )

# Dicionário de meses.
DictMesesBusca = { 'JANEIRO': '01', 
                   'FEVEREIRO': '02', 
                   'MARÇO': '03', 
                   'ABRIL': '04', 
                   'MAIO': '05', 
                   'JUNHO': '06', 
                   'JULHO': '07', 
                   'AGOSTO': '08', 
                   'SETEMBRO': '09', 
                   'OUTUBRO': '10', 
                   'NOVEMBRO': '11', 
                   'DEZEMBRO': '12' }

# Filtro para serviço.
filtro_servico = st.sidebar.multiselect( 'Serviço', pagamentos[ 'SERVIÇO' ].unique() ) # criando seleção múltipla com todas as opções de serviços.

if filtro_servico:
    pagamentos = pagamentos[ pagamentos[ 'SERVIÇO' ].isin( filtro_servico ) ]

# Check para ver se eu quero considerar o arquiteto na conta ou não.
checkGCO = st.sidebar.checkbox( 'Considera GCO?', value = True ) # check box com o default em True.
if not checkGCO:
    pagamentos = pagamentos[ pagamentos[ 'SERVIÇO' ] != 'S01 - 16- GCO' ]

# Transformando.
pagamentos[ 'MES' ] = pagamentos[ 'MES' ].apply( lambda x: DictMesesBusca[ x ] )

# Criando Ano Mês.
pagamentos[ 'MES_ANO' ] = pagamentos[ 'ANO' ] + ' - ' + pagamentos[ 'MES' ] 


    #         #
    # Tabelas #
    #         #  

# Visão por mês de gasto.
gastos_mensais = pagamentos.groupby( [ 'MES_ANO' ] )[ [ 'VALOR' ] ].sum().reset_index().sort_values( 'MES_ANO' )

# Visão por tipo de serviço.
gastos_por_servico = pagamentos.groupby( [ 'SERVIÇO' ] )[ [ 'VALOR' ] ].sum().reset_index()

# Visão de serviço e mês de gasto.
gastos_por_mes_e_servico = pagamentos.groupby( [ 'MES_ANO', 'SERVIÇO' ] )[ [ 'VALOR' ] ].sum().reset_index().sort_values( 'MES_ANO' )


    #          #
    # Gráficos #
    #          #

# Gráfico de gastos por mês.
fig1 = px.bar( gastos_mensais, 
               x = 'MES_ANO', 
               y = 'VALOR', 
               template = 'seaborn',
               title = 'Gastos por Mês', 
               text_auto = False,
               category_orders = { 'MES_ANO': sorted( gastos_mensais.MES_ANO.unique() ) },
               labels = { 'MES_ANO': 'Mês', 'VALOR': 'Valor Financeiro' } )

# Padrão de dinheiro.
fig1.update_layout( yaxis_tickprefix = 'R$', yaxis_tickformat = ',.2f' )
fig1.update_xaxes( tickangle = -45 ) # colocando rotação no eixo X.

# Gráfico de gastos por serviço.
fig2 = px.bar( gastos_por_servico, 
               x = 'SERVIÇO', 
               y = 'VALOR', 
               template = 'seaborn',
               title = 'Gastos por Serviço', 
               text_auto = False,
               labels = { 'SERVIÇO': 'Serviço', 'VALOR': 'Valor Financeiro' } )

# Padrão de dinheiro.
fig2.update_layout( yaxis_tickprefix = 'R$', yaxis_tickformat = ',.2f' )
fig2.update_xaxes( tickangle = -45 ) # colocando rotação no eixo X.

# Gráfico de gastos relativos por mês e serviço.
fig3 = px.histogram( gastos_por_mes_e_servico, 
                     x = 'MES_ANO', 
                     y = 'VALOR', 
                     color = 'SERVIÇO', 
                     barnorm = 'percent', 
                     text_auto = '.2f', 
                     title = 'Gastos Percentuais por Mês',
                     category_orders = { 'MES_ANO': sorted( gastos_por_mes_e_servico.MES_ANO.unique() ) },
                     labels = { 'MES_ANO': 'Mês', 'VALOR': '%' } )

fig3.update_xaxes( tickangle = -45 ) # colocando rotação no eixo X.
fig3.update_layout( yaxis_title_text = '%' ) # mudando nome do eixo Y.


    #              #    
    # Visualização #
    #              #

aba1, aba2 = st.tabs( [ 'Gastos Totais', 'Gastos Relativos' ] ) # criando abas.

# coluna1 = st.columns( [ 1 ] ) # criando 2 colunas.

with aba1:
    st.metric( 'Gasto Total', formata_numero( gastos_mensais[ 'VALOR' ].sum(), 'R$' ) )
    st.plotly_chart( fig1, use_container_width = True ) # preenche o chart no tamanho da coluna.
    st.plotly_chart( fig2, use_container_width = True ) # preenche o chart no tamanho da coluna.

with aba2:
    st.plotly_chart( fig3, use_container_width = True ) # preenche o chart no tamanho da coluna.

