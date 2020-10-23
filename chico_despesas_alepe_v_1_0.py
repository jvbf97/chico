#Scrapping portal da transparência de pernambuco / Despesas detalhadas

import requests
import json
import pandas as pd

columns = []
rows = []

for i in range(2008,2030):

    #Parâmetros do post request da página(pegos na aba de desenvolvedor > Network)
    payload = {'paramlimit_':'99999', 'paramoffset_':'0', 'parampara_ano':str(i), 'parampara_ug':'0', 'parampara_empenho':'', 'parampara_categoria':'0', 'parampara_grupo':'0', 'parampara_orgao':'1000', 'parampara_modalidade':'0', 'parampara_elemento':'0', 'paramativa':'', 'parampara_funcao':'%%', 'parampara_acao':'%%', 'parampesquisa_':'', 'parampesquisa_emp':'', 'parampesquisa_obs':'', 'parampara_ano_emp':'0', 'parampara_subfuncao':'%%', 'parampara_programa':'%%', 'parampara_subacao':'%%', 'parampara_fonte':'%%', 'parampara_inicio_emp':'', 'parampara_fim_emp':'', 'parampara_ficha':'%%', 'path':'/public/OpenReports/Portal_Producao/Painel_Despesas_Detalhamento/Painel_Despesa_Detalhamento.cda', 'dataAccessId':'select_tabela_empenho', 'outputIndexId':'1', 'pageSize':'0', 'pageStart':'0', 'sortBy':'', 'paramsearchBox':''}
    #url do post request
    r = requests.post('http://web.transparencia.pe.gov.br/pentaho/plugin/cda/api/doQuery', data=payload)

    rJson = json.loads(r.text)

    #iterando entre as linhas e colocando numa lista
    for row in rJson['resultset']:
        row.append(str(i))
        rows.append(row)

    #colocando os nomes das colunas numa lista
    if i == 2008:
        for item in rJson['metadata']:
            columns.append(item['colName'])
    else:
        pass

    print(str(i) + " " + "Done")

#Adicionando a coluna Ano
columns.append('Ano')

#Escrevendo as linhas e colunas do dataframe
df = pd.DataFrame(rows)
df.columns = columns

# Algumas alterações nas colunas
df['CPF/CNPJ'], df['credor'] = df['?column?'].str.split(' - ', 1).str
df['num_elemento'], df['elemento'] = df['cd_nm_elemento'].str.split(' - ', 1).str
df['num_acao'], df['acao'] = df['cd_nm_acao'].str.split(' - ', 1).str
df['num_programa'], df['programa'] = df['cd_nm_prog'].str.split(' - ', 1).str

df.drop(['cd_nm_elemento','cd_nm_acao','cd_nm_prog','?column?'], axis = 1, inplace = True)

#Ajustando números
df['vlrtotalpago'] = df.apply(lambda x: "{:,}".format(x['vlrtotalpago']), axis=1)
df['vlrempenhado'] = df.apply(lambda x: "{:,}".format(x['vlrempenhado']), axis=1)
df['vlrliquidado'] = df.apply(lambda x: "{:,}".format(x['vlrliquidado']), axis=1)

df.to_csv('despesas_detalhadas.csv', index = False)

print("Arquivo pronto")
