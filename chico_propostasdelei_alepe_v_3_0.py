#Scrapping propostas de lei da ALEPE

import requests
import pandas as pd
from bs4 import BeautifulSoup
import time

#Número de páginas

url = 'http://www.alepe.pe.gov.br/proposicoes/'

payload = {'pagina':'1', 'field-tipo-filtro':'projetos', 'field-proposicoes-filtro':'numero',
'field-proposicoes':'', 'field-proposicoes2':'', 'field-comissoes' :'', 'field-palavrachave':''}

response = requests.post(url, data = payload)

soup = BeautifulSoup(response.text, 'html.parser')

num_paginas = int(soup.find('div', class_='pages').find_all('a')[-1].text) + 1

#Obter informação de todas as tabelas das paginas

tables = [] #lista das tabelas de cada página
links = [] #lista com todos os links

print('Iniciando captura de tabelas ')
print('O total de páginas é ' + str(num_paginas))

for page in range(1,num_paginas):

    #Parâmetros do post request da página (field-tipo-filtro = projetos para pegar apenas projetos de lei)
    payload = {'pagina':str(page), 'field-tipo-filtro':'projetos', 'field-proposicoes-filtro':'numero',
    'field-proposicoes':'', 'field-proposicoes2':'', 'field-comissoes' :'', 'field-palavrachave':''}

    response = requests.post(url, data = payload)

    soup = BeautifulSoup(response.text, 'html.parser')

    table_html = soup.find('table')

    #Criar lista de tabelas
    table = pd.read_html(str(table_html))

    #Armazenar tabelas
    for item in table:
        tables.append(item)

    #Armazenar links
    linhas = soup.find('tbody').find_all('tr')

    for tr in linhas:
        link = 'http://www.alepe.pe.gov.br' + tr.contents[3].a['href']
        links.append(link)

    #mostrar progresso

    print('tabela da pagina' + ' ' + str(page) + ' ' + 'completa')

#Juntar lista de tabelas numa tabela consolidada

df_tabela_propostas = pd.concat(tables, ignore_index = True)
df_tabela_propostas['Link'] = links

#Iniciar captura tos textos relativos as propostas de lei
print(' ')
print('Iniciando captura dos textos')

relatorio_propostas = [] #armazenar os dados
numero_extracao = 0 #contagem

for i in df_tabela_propostas['Link']:

    numero_extracao = numero_extracao + 1 #contagem
    pagina = requests.get(i).text
    obj = BeautifulSoup(pagina, 'html.parser')

    titulo = obj.find("div", {"class":"proposicao-list-header"}).h2.text
    linkproposta = i

    print("(",numero_extracao,"de",len(df_tabela_propostas['Link'].tolist()),")", titulo,)

    if len(obj.find_all("div", {"class":"proposicao-list-item"}))<4:
        resumo = "".join(str(tuple(obj.find("div", {"class":"proposicao-list-header"}).p)).replace("\n", " ").replace("|", " ").replace("<br/>", " ").replace("<br>", "").replace(".....", ""))
        textocompleto = "".join(str(tuple(obj.find_all("div", {"class":"proposicao-list-item-text"})[0])).replace("\n", " ").replace("|", " ").replace("<br/>", " ").replace("<br>", "").replace(".....", ""))
        justificativa = "nenhum"
        historico = "".join(str(tuple(obj.find_all("div", {"class":"proposicao-list-item-text"})[1])).replace("\n", " ").replace("|", " ").replace("<br/>", " ").replace("<br>", "").replace(".....", ""))
    else:
        resumo = "".join(str(tuple(obj.find("div", {"class":"proposicao-list-header"}).p)).replace("\n", " ").replace("|", " ").replace("<br/>", " ").replace("<br>", "").replace(".....", ""))
        textocompleto = "".join(str(tuple(obj.find_all("div", {"class":"proposicao-list-item-text"})[0])).replace("\n", " ").replace("|", " ").replace("<br/>", " ").replace("<br>", "").replace(".....", ""))
        justificativa = "".join(str(tuple(obj.find_all("div", {"class":"proposicao-list-item-text"})[1])).replace("\n", " ").replace("|", " ").replace("<br/>", " ").replace("<br>", "").replace(".....", ""))
        historico = "".join(str(tuple(obj.find_all("div", {"class":"proposicao-list-item-text"})[2])).replace("\n", " ").replace("|", " ").replace("<br/>", " ").replace("<br>", "").replace(".....", ""))

#dados de situação e aprovações
    try:
        situacao = obj.find_all("table", {"class":"table table-proposicao"})[0].tbody.find_all('td')[1].text
    except:
        situação = "Não informado"
    try:
        localizacao = obj.find_all("table", {"class":"table table-proposicao"})[0].tbody.find_all('td')[3].text
    except:
        localizacao = "Não informado"
#tramitação
    try:
        primeira_publicacao_data = obj.find_all("table", {"class":"table table-proposicao"})[1].tbody.find_all('td')[1].text
    except:
        primeira_publicacao_data = "Não informado"
    try:
        primeira_publicacao_OD_data = obj.find_all("table", {"class":"table table-proposicao"})[1].tbody.find_all('tr')[1].find_all('td')[1].text
    except:
        primeira_publicacao_OD_data = "Não informado"

#sessão plenária
    try:
        sec_plenario_primeira_resultado = obj.find_all("table", {"class":"table table-proposicao"})[2].tbody.find_all('tr')[0].find_all('td')[1].text
    except:
        sec_plenario_primeira_resultado = "Não informado"
    try:
        sec_plenario_primeira_data = obj.find_all("table", {"class":"table table-proposicao"})[2].tbody.find_all('tr')[0].find_all('td')[3].text
    except:
        sec_plenario_primeira_data = "Não informado"
    try:
        sec_plenario_segunda_resultado = obj.find_all("table", {"class":"table table-proposicao"})[2].tbody.find_all('tr')[1].find_all('td')[1].text
    except:
        sec_plenario_segunda_resultado = "Não informado"
    try:
        sec_plenario_segunda_data = obj.find_all("table", {"class":"table table-proposicao"})[2].tbody.find_all('tr')[1].find_all('td')[3].text
    except:
        sec_plenario_segunda_data = "Não informado"

#resultado final
    try:
        redacao_final_data = obj.find_all("table", {"class":"table table-proposicao"})[3].tbody.find_all('tr')[0].find_all('td')[1].text
    except:
        redacao_final_data = "Não informado"
    try:
        redacao_final_resultado = obj.find_all("table", {"class":"table table-proposicao"})[3].tbody.find_all('tr')[2].find_all('td')[1].text
    except:
        redacao_final_resultado = "Não informado"
    try:
        redacao_final_resultado_data = obj.find_all("table", {"class":"table table-proposicao"})[3].tbody.find_all('tr')[2].find_all('td')[3].text
    except:
        redacao_final_resultado_data = "Não informado"

#contar o número de documentos relacionados:
    try:
        checardocumentos = obj.find("div", {"class":"msg-aviso"})["class"][0]
    except:
        checardocumentos = "existem documentos"

    if checardocumentos == "msg-aviso":
        numero_linhas_documentos = 0
    else:
        numero_linhas_documentos = len(obj.find_all("table", {"class":"table"})[-1].tbody.find_all('tr'))

#extrair os dados de documentos relacionados:

#Primeira linha
    if numero_linhas_documentos > 0:
        doc_um_tipo = obj.find_all("table", {"class":"table"})[-1].tbody.find_all('tr')[0].find_all('td')[0].text
        doc_um_numero = obj.find_all("table", {"class":"table"})[-1].tbody.find_all('tr')[0].find_all('td')[1].text
        doc_um_autor = obj.find_all("table", {"class":"table"})[-1].tbody.find_all('tr')[0].find_all('td')[2].text
        doc_um_link = "http://www.alepe.pe.gov.br" + obj.find_all("table", {"class":"table"})[-1].tbody.find_all('tr')[0].find_all('td')[1].a['href']
    else:
        doc_um_tipo = "nenhum"
        doc_um_numero = "nenhum"
        doc_um_autor = "nenhum"
        doc_um_link = "nenhum"

#segunda linha
    if numero_linhas_documentos > 1:
        doc_dois_tipo = obj.find_all("table", {"class":"table"})[-1].tbody.find_all('tr')[1].find_all('td')[0].text
        doc_dois_numero = obj.find_all("table", {"class":"table"})[-1].tbody.find_all('tr')[1].find_all('td')[1].text
        doc_dois_autor = obj.find_all("table", {"class":"table"})[-1].tbody.find_all('tr')[1].find_all('td')[2].text
        doc_dois_link = "http://www.alepe.pe.gov.br" + obj.find_all("table", {"class":"table"})[-1].tbody.find_all('tr')[1].find_all('td')[1].a['href']
    else:
        doc_dois_tipo = "nenhum"
        doc_dois_numero = "nenhum"
        doc_dois_autor = "nenhum"
        doc_dois_link = "nenhum"

#terceira linha
    if numero_linhas_documentos > 2:
        doc_tres_tipo = obj.find_all("table", {"class":"table"})[-1].tbody.find_all('tr')[2].find_all('td')[0].text
        doc_tres_numero = obj.find_all("table", {"class":"table"})[-1].tbody.find_all('tr')[2].find_all('td')[1].text
        doc_tres_autor = obj.find_all("table", {"class":"table"})[-1].tbody.find_all('tr')[2].find_all('td')[2].text
        doc_tres_link = "http://www.alepe.pe.gov.br" + obj.find_all("table", {"class":"table"})[-1].tbody.find_all('tr')[2].find_all('td')[1].a['href']
    else:
        doc_tres_tipo = "nenhum"
        doc_tres_numero = "nenhum"
        doc_tres_autor = "nenhum"
        doc_tres_link = "nenhum"

#quarta linha
    if numero_linhas_documentos > 3:
        doc_quarta_tipo = obj.find_all("table", {"class":"table"})[-1].tbody.find_all('tr')[3].find_all('td')[0].text
        doc_quarta_numero = obj.find_all("table", {"class":"table"})[-1].tbody.find_all('tr')[3].find_all('td')[1].text
        doc_quarta_autor = obj.find_all("table", {"class":"table"})[-1].tbody.find_all('tr')[3].find_all('td')[2].text
        doc_quarta_link = "http://www.alepe.pe.gov.br" + obj.find_all("table", {"class":"table"})[-1].tbody.find_all('tr')[3].find_all('td')[1].a['href']
    else:
        doc_quarta_tipo = "nenhum"
        doc_quarta_numero = "nenhum"
        doc_quarta_autor = "nenhum"
        doc_quarta_link = "nenhum"

#quinta linha
    if numero_linhas_documentos > 4:
        doc_quinta_tipo = obj.find_all("table", {"class":"table"})[-1].tbody.find_all('tr')[4].find_all('td')[0].text
        doc_quinta_numero = obj.find_all("table", {"class":"table"})[-1].tbody.find_all('tr')[4].find_all('td')[1].text
        doc_quinta_autor = obj.find_all("table", {"class":"table"})[-1].tbody.find_all('tr')[4].find_all('td')[2].text
        doc_quinta_link = "http://www.alepe.pe.gov.br" + obj.find_all("table", {"class":"table"})[-1].tbody.find_all('tr')[4].find_all('td')[1].a['href']
    else:
        doc_quinta_tipo = "nenhum"
        doc_quinta_numero = "nenhum"
        doc_quinta_autor = "nenhum"
        doc_quinta_link = "nenhum"

#sexta linha
    if numero_linhas_documentos > 5:
        doc_sexta_tipo = obj.find_all("table", {"class":"table"})[-1].tbody.find_all('tr')[5].find_all('td')[0].text
        doc_sexta_numero = obj.find_all("table", {"class":"table"})[-1].tbody.find_all('tr')[5].find_all('td')[1].text
        doc_sexta_autor = obj.find_all("table", {"class":"table"})[-1].tbody.find_all('tr')[5].find_all('td')[2].text
        doc_sexta_link = "http://www.alepe.pe.gov.br" + obj.find_all("table", {"class":"table"})[-1].tbody.find_all('tr')[5].find_all('td')[1].a['href']
    else:
        doc_sexta_tipo = "nenhum"
        doc_sexta_numero = "nenhum"
        doc_sexta_autor = "nenhum"
        doc_sexta_link = "nenhum"

#setima linha
    if numero_linhas_documentos > 6:
        doc_setima_tipo = obj.find_all("table", {"class":"table"})[-1].tbody.find_all('tr')[6].find_all('td')[0].text
        doc_setima_numero = obj.find_all("table", {"class":"table"})[-1].tbody.find_all('tr')[6].find_all('td')[1].text
        doc_setima_autor = obj.find_all("table", {"class":"table"})[-1].tbody.find_all('tr')[6].find_all('td')[2].text
        doc_setima_link = "http://www.alepe.pe.gov.br" + obj.find_all("table", {"class":"table"})[-1].tbody.find_all('tr')[6].find_all('td')[1].a['href']
    else:
        doc_setima_tipo = "nenhum"
        doc_setima_numero = "nenhum"
        doc_setima_autor = "nenhum"
        doc_setima_link = "nenhum"

    relatorio_propostas.append((
    linkproposta,
    titulo,
    resumo,
    textocompleto,
    justificativa,
    historico,
    situacao,
    localizacao,
    primeira_publicacao_data,
    primeira_publicacao_OD_data,
    sec_plenario_primeira_resultado,
    sec_plenario_primeira_data,
    sec_plenario_segunda_resultado,
    sec_plenario_segunda_data,
    redacao_final_data,
    redacao_final_resultado,
    redacao_final_resultado_data,
    numero_linhas_documentos,
    doc_um_tipo,
    doc_um_numero,
    doc_um_autor,
    doc_um_link,
    doc_dois_tipo,
    doc_dois_numero,
    doc_dois_autor,
    doc_dois_link,
    doc_tres_tipo,
    doc_tres_numero,
    doc_tres_autor,
    doc_tres_link,
    doc_quarta_tipo,
    doc_quarta_numero,
    doc_quarta_autor,
    doc_quarta_link,
    doc_quinta_tipo,
    doc_quinta_numero,
    doc_quinta_autor,
    doc_quinta_link,
    doc_sexta_tipo,
    doc_sexta_numero,
    doc_sexta_autor,
    doc_sexta_link,
    doc_setima_tipo,
    doc_setima_numero,
    doc_setima_autor,
    doc_setima_link,
    ))

#Criar dataframe e exportar csv file
df_relatorio = pd.DataFrame(relatorio_propostas,columns=[
"linkproposta",
"titulo",
"resumo",
"textocompleto",
"justificativa",
"historico",
"situacao",
"localizacao",
"primeira_publicacao_data",
"primeira_publicacao_OD_data",
"sec_plenario_primeira_resultado",
"sec_plenario_primeira_data",
"sec_plenario_segunda_resultado",
"sec_plenario_segunda_data",
"redacao_final_data",
"redacao_final_resultado",
"redacao_final_resultado_data",
"numero_linhas_documentos",
"doc_um_tipo",
"doc_um_numero",
"doc_um_autor",
"doc_um_link",
"doc_dois_tipo",
"doc_dois_numero",
"doc_dois_autor",
"doc_dois_link",
"doc_tres_tipo",
"doc_tres_numero",
"doc_tres_autor",
"doc_tres_link",
"doc_quarta_tipo",
"doc_quarta_numero",
"doc_quarta_autor",
"doc_quarta_link",
"doc_quinta_tipo",
"doc_quinta_numero",
"doc_quinta_autor",
"doc_quinta_link",
"doc_sexta_tipo",
"doc_sexta_numero",
"doc_sexta_autor",
"doc_sexta_link",
"doc_setima_tipo",
"doc_setima_numero",
"doc_setima_autor",
"doc_setima_link",
])

#juntar as informaçõoes num único dataframe

#dfconsolidado = df_relatorio.merge(df_tabela_propostas, left_on='Link', right_on='linkproposta', how='left')

dfconsolidado = pd.merge(df_relatorio,df_tabela_propostas, left_on='linkproposta', right_on='Link', how='left')


dfconsolidado.to_excel('propostas_de_leis.xlsx', index = False)
print(' ')
print("Arquivo pronto")

