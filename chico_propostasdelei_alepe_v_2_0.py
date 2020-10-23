import time
from selenium import webdriver
from bs4 import BeautifulSoup
import datetime
from time import gmtime, strftime
import pandas as pd
import sys
import requests
import os
import csv

#1.0 Cria os diretórios para armazenar os arquivos .csv (ALEPE/[Data-da-extração-dos-dados])
dirName = strftime('%Y-%m-%d')

try:
    os.makedirs(dirName)
    print("Diretório " , dirName ,  " criado! ")
except FileExistsError:
    print("Diretório " , dirName ,  " já existe!")

#cria a lista que será utilizada para armazenar os dados relevantes
listapropostas = []

#abrir a primeira página
#driver = webdriver.Chrome('/Users/Mac/Desktop/Pedro/chromedriver')
driver = webdriver.Chrome(r'C:\Users\jvbf9\Documents\cidadaofiscal\Alepe\projetos de leis\chromedriver_win32\chromedriver')
driver.get('http://www.alepe.pe.gov.br/proposicoes/#')

#Selecionar os parâmetros da página

selecioneprojeto = driver.find_element_by_id('field-tipo-filtro')
selecioneprojeto.send_keys('projetos')

selecionenome = driver.find_element_by_id('field-proposicoes2')
selecionenome.clear()
driver.find_elements_by_css_selector("a.button")[0].click()

#time.sleep(3)

#Extrair o conteúdo HTML da primeira página
doc = driver.page_source
soup = BeautifulSoup(doc, 'html.parser')

results = soup.find('tbody').find_all('tr')


#Salvar os dados em uma tabela
for x in results:
    autor = x.contents[1].text
    proposicao = x.contents[3].text
    data = x.contents[5].text
    link = "http://www.alepe.pe.gov.br" + x.contents[3].a['href']
    listapropostas.append([autor, proposicao, data, link])

#Repetir o mesmo trabalho para todas as outras páginas

#time.sleep(3)
numerodepaginas = int(soup.find('div', {'class':'pages'}).find_all('a')[-1].text)
proximapagina = 2
listapaginas = list(range(proximapagina, numerodepaginas+1))

for pag in listapaginas:
    driver.find_element_by_link_text(str(pag)).click()
    time.sleep(3)

    #Extrair o conteúdo HTML da segunda página
    doc = driver.page_source
    soup = BeautifulSoup(doc, 'html.parser')
    results = soup.find('tbody').find_all('tr')

    #Salvar os dados em uma tabela
    for x in results:
        autor = x.contents[1].text
        proposicao = x.contents[3].text
        data = x.contents[5].text
        link = "http://www.alepe.pe.gov.br" + x.contents[3].a['href']
        listapropostas.append([autor, proposicao, data, link])


#salvar a lista em um arquivo .csv
dflistapropostas = pd.DataFrame(listapropostas, columns=["Autor","Proposta de Lei","Data","Link"])
listapropostas_csv = 'listapropostas.csv'
dflistapropostas.to_csv(listapropostas_csv, index = False, sep='|')
os.rename(listapropostas_csv, dirName+'/'+listapropostas_csv)

#time.sleep(5)
driver.quit()


############################### INÍCIO CAPTURA DOS DADOS ###############################

#lista_paginas_propostas=[listapropostas['Link']]

#criar a lista que será utilizada para armanezar os dados relevantes
relatorio_propostas = []
numero_extracao = 0
#Importa a lista de todas as páginas a serem extraidas
lista_paginas_propostas = dflistapropostas["Link"].tolist()


#Extrai o conteúdo da página
for x in lista_paginas_propostas:
    numero_extracao = numero_extracao + 1
    pagina = requests.get(x).text
    obj = BeautifulSoup(pagina, 'html.parser')
#conteúdo da proposta de lei
    linkproposta = x
    titulo = obj.find("div", {"class":"proposicao-list-header"}).h2.text
    print("(",numero_extracao,"de",len(lista_paginas_propostas),")", titulo,)


#Checar se existe a info "Justificativa":
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
dfpropostas = pd.DataFrame(relatorio_propostas,columns=[
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


#exportar dados das propostas para um excel
report_dados_propostas_excel = 'report_dados_propostas.xlsx'
dfpropostas.to_excel(report_dados_propostas_excel, index=False)
os.rename(report_dados_propostas_excel, dirName+'/'+report_dados_propostas_excel)


# Fazer um merge dos dataframes e exportar um excel com o relatório final

dfconsolidado = dfpropostas.merge(dflistapropostas, left_on='Link', right_on="linkproposta", how='left')
relatoriofinal_nome_excel = 'consolidado_propostas_dados.xlsx'
dfconsolidado.to_excel(relatoriofinal_nome_excel , index=False)
os.rename(relatoriofinal_nome_excel, dirName+'/'+relatoriofinal_nome_excel)
