from bs4 import BeautifulSoup
import requests
import pandas as pd
import csv
import datetime
from time import gmtime, strftime
import itertools
import os

#1.0 Cria os diretórios para armazenar os arquivos .csv (ALEPE/[Data-da-extração-dos-dados])
dirName = 'alepe/vi/'+strftime('%Y-%m-%d')

try:
    os.makedirs(dirName)    
    print("Diretório " , dirName ,  " criado! ")
except FileExistsError:
    print("Diretório " , dirName ,  " já existe!")  

#2.0 script para buscar todos os 'docid' de um determinado ano e mês

lista_ano = ['2011','2012','2013','2014','2015','2016','2017','2018','2019','2020']
lista_mes = ['1','2','3','4','5','6','7','8','9','10','11','12']
relatorio_docid = []
contagem_pagina_docid = 0

for a in lista_ano:
    for b in lista_mes:
        docid_json = requests.get('http://www.alepe.pe.gov.br/servicos/transparencia/adm/verbaindenizatoria.php?ano='+a+'&mes='+b).json()
        contagem_pagina_docid = contagem_pagina_docid + 1
        for c in docid_json:
            docid_import = strftime('%Y-%m-%d %H:%M:%S')
            docid_docid = c['docid']
            docid_numero = c['numero']
            docid_tipo = c['tipo']
            docid_ano = c['ano']
            docid_parlamentar = c['deputado']
            docid_mes = c['mes']
            docid_total = c['total']
            docid_linkdadosnotas = "http://www.alepe.pe.gov.br/servicos/transparencia/adm/verbaindenizatorianotas.php?docid="+docid_docid
            relatorio_docid.append((docid_import, docid_docid, docid_numero, docid_tipo, docid_ano, docid_parlamentar, docid_mes, docid_total,docid_linkdadosnotas))
            print(strftime('%Y-%m-%d %H:%M:%S')," (",(contagem_pagina_docid)," de", len(lista_ano)*len(lista_mes),"...",round(contagem_pagina_docid/(len(lista_ano)*len(lista_mes)),2)*100,"%)", docid_parlamentar,docid_ano,docid_mes)

#Criar dataframe e exportar csv file    
dfdocid= pd.DataFrame(relatorio_docid, columns=["dataimport","docid", "numero", "tipo", "ano","parlamentar","mes","total","linkdadosnotas"])
docid_csv = 'relatorio_docid_alepe_vi.csv'
dfdocid.to_csv(docid_csv, index = False, sep='|')
os.rename(docid_csv, dirName+'/'+docid_csv)


#################
# 3.0 script para capturar os dados de todas as notas fiscais de um Docid

listapaginasdocid = []

for d in relatorio_docid:
        listapaginasdocid.append(d[8])

relatorio_notas = []
contagem_pagina_notas = 0

for e in listapaginasdocid:
    notas_json = requests.get(e).json()
    contagem_pagina_notas = contagem_pagina_notas + 1
    for f in notas_json:
        nota_docid = e.strip('http://www.alepe.pe.gov.br/servicos/transparencia/adm/verbaindenizatorianotas.php?docid=')
        nota_data_import = strftime('%Y-%m-%d %H:%M:%S')
        nota_rubrica = f['rubrica']
        nota_sequencial = f['sequencial']
        nota_data = f['data']
        nota_cnpj = f['cnpj']
        nota_empresa = f['empresa']
        nota_valor = f['valor']
        relatorio_notas.append((nota_data_import,nota_rubrica,nota_sequencial,nota_data,nota_cnpj,nota_empresa,nota_valor, nota_docid))
        print(strftime('%Y-%m-%d %H:%M:%S')," (",(contagem_pagina_notas)," de", len(listapaginasdocid),"...",round(contagem_pagina_notas/len(listapaginasdocid),2)*100,"%)",nota_docid)

#Criar dataframe e exportar csv file    
dfnotas= pd.DataFrame(relatorio_notas, columns=["dataimport","rubrica", "sequencial", "data","cnpj","empresa","valor","docid"])
notas_csv = 'relatorio_notas_alepe_vi.csv'
dfnotas.to_csv(notas_csv, index = False, sep='|')
os.rename(notas_csv, dirName+'/'+notas_csv)  

######## Último Passo ######

# 4.0 Fazer um merge dos dataframes de Pedidos e Notas para obter apenas 1 df + 1 csv consolidando todas as informações que precisamos

dfconsolidado = dfnotas.merge(dfdocid, on='docid', how='left')
relatoriofinal_csv = 'relatorio_consolidado_alepe_vi.csv'
dfconsolidado.to_csv(relatoriofinal_csv , index=False, sep='|')
os.rename(relatoriofinal_csv, dirName+'/'+relatoriofinal_csv) 
