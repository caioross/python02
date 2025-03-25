import pandas as pd

# Carregar os dados da planilha do Excel
caminho = 'C:/Users/noturno/Desktop/Caio2/01_base_vendas.xlsx'

df1 = pd.read_excel(caminho, sheet_name='Relatório de Vendas')
df2 = pd.read_excel(caminho, sheet_name='Relatório de Vendas1')

# Exibir as primeiras linhas para conferir como estão os dados
print('Primeiro Relatorio')
print(df1.head())

print('Segundo Relatorio')
print(df2.head())

# Verificar se há duplicatas nas duas tabelas
print('Duplicados no relatorio de vendas')
print(df1.duplicated().sum())

print('Duplicados no relatorio de vendas 2:')
print(df2.duplicated().sum())

#  Agora vamos fazer o merge das duas planilhas
df_consolidado = pd.concat([df1,df2], ignore_index=True)
print('Dados consolidados:')
print(df_consolidado.head())

# Exibir o numero de clientes por cidade
clientes_por_cidade = df_consolidado.groupby('Cidade')['Cliente'].nunique().sort_values(ascending=False)
print('\n Clientes por cidade:')
print(clientes_por_cidade)

# Exibir o numero de vendas por plano
vendas_por_plano = df_consolidado['Plano Vendido'].value_counts()
print('\n Numero de vendas por plano:')
print(vendas_por_plano)

# Exibir as 3 primeiras cidades com mais clientes
top_3_cidades  = clientes_por_cidade.head(3)
print('\n Top 3 cidades')
print(top_3_cidades)

# Exibir o total de clientes
total_clientes = df_consolidado['Cliente'].nunique()
print(f'\n Numero total de clientes: {total_clientes}')

# Adicionar uma coluna de "Status" (exemplo ficticio de analise)
# Vamos classificar os planos como "Premium" se for "Enterprise", caso contrario "Padrão"
df_consolidado['Status'] = df_consolidado['Plano Vendido'].apply(lambda x: 'Premium' if x == 'Enterprise' else 'Padrão')

# Exibir a distribuição do Status
status_dist =  df_consolidado['Status'].value_counts()
print('\n Distribuição de Status dos Planos:')
print(status_dist)

# Agora vamos salvar o dataframe consolidado em dois formatos:
# Salvando em Excel
df_consolidado.to_excel('dados_consolidados_planilha.xlsx', index=False)

# Salvando em CSV
df_consolidado.to_csv('dados_consolidados_texto.csv', index=False)

# Exibir mensagem final!!!!!
print('\n Arquivos foram gerados com sucesso!!! ')