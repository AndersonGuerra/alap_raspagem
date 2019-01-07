# para obter os meses disponiveis em um ano, é necessário enviar via post
# para o seuinte endereço: http://www.al.ap.gov.br/transparencia/mes_ceap_json.php
# com ano_verbaB: anoDesejado (form url encoded)

# para obter os gabinetes disponíveis em um mês específico, enviar via post
# para http://www.al.ap.gov.br/transparencia/gabinete_ceap_json.php
# com ano_verbaB: anoDesejado e mes_verbaB: mesDesejado (mês com dois digitos, a partir de 01)

# para obter os gastos de um deputado em um mes especifico, enviar via post
# para http://www.al.ap.gov.br/transparencia/index.php?pg=ceap&acao=buscar
# com ano_verbaB: anoDesejado e mes_verbaB: mesDesejado (mês com dois digitos, a partir de 01) e idgabineteB: idGabinete

import xlsxwriter
import requests
from bs4 import BeautifulSoup

url_base = "http://www.al.ap.gov.br/transparencia/"
url_getMeses = "http://www.al.ap.gov.br/transparencia/mes_ceap_json.php"
url_getGabinetes = "http://www.al.ap.gov.br/transparencia/gabinete_ceap_json.php"
url_buscar = "http://www.al.ap.gov.br/transparencia/index.php?pg=ceap&acao=buscar"
linha_counter = 1
meses = {
    '01': 'Janeiro',
    '02': 'Fevereiro',
    '03': 'Março',
    '04': 'Abril',
    '05': 'Maio',
    '06': 'Junho',
    '07': 'Julho',
    '08': 'Agosto',
    '09': 'Setembro',
    '10': 'Outubro',
    '11': 'Novembro',
    '12': 'Dezembro'
}

data_getMeses = {'ano_verbaB': ''}

ano_desejado = input("Insira o ano desejado para raspagem: ")
data_getMeses['ano_verbaB'] = ano_desejado
responseMeses = requests.post(url_getMeses, data=data_getMeses)
meses_lista = []
for option in BeautifulSoup(responseMeses.text).find_all('option'):
    meses_lista.append(option['value'])
meses_lista = meses_lista[1:]

planilha = xlsxwriter.Workbook(f'alap_ceap_{ano_desejado}.xlsx')
worksheet = planilha.add_worksheet()
worksheet.write(0, 0, 'DESPESA')
worksheet.write(0, 1, 'VALOR')
worksheet.write(0, 2, 'GABINETE DEPUTADO')
worksheet.write(0, 3, 'MÊS/ANO')

try:
    for mes in meses_lista:
        # para cada mes é preciso pegar a lista de gabinetes
        data_getGabinetes = {'ano_verbaB': ano_desejado, 'mes_verbaB': mes}
        responseGabinetes = requests.post(url_getGabinetes, data=data_getGabinetes)
        gabinetes_lista = []
        for option in BeautifulSoup(responseGabinetes.text).find_all('option'):
            gabinetes_lista.append(option['value'])
        gabinetes_lista = gabinetes_lista[1:]
        for gabinete in gabinetes_lista:
            data_gab_gastos = {'ano_verbaB': ano_desejado, 'mes_verbaB': mes, 'idgabineteB': gabinete}
            response_gab_gastos = requests.post(url_buscar, data=data_gab_gastos)
            print('Tamanho da tabela ' + str(len(BeautifulSoup(response_gab_gastos.text).findChildren('table'))) + ". Deputado: "+str(gabinete) + ". Mês: " + str(mes))
            if (len(BeautifulSoup(response_gab_gastos.text).findChildren('table')) == 0):
                continue
            tabela_despesa = BeautifulSoup(response_gab_gastos.text).findChildren('table')[0].find('tbody')
            linhas_tabela = tabela_despesa.findChildren('tr')
            gastoMensal = []
            for linha in linhas_tabela:
                gasto = {}
                celulas = linha.findChildren('td')
                link = linha.findChildren('a')
                if (link):
                    gasto['link'] = url_base + link[0]['href']
                
                gasto['despesa'] = celulas[0].string
                gasto['valor'] = celulas[1].string
                
                gasto['mes'] = meses[mes]
                gasto['ano'] = ano_desejado
                gastoMensal.append(gasto)
            gastoMensal = gastoMensal[:-1]
            for gasto in gastoMensal:
                worksheet.write(linha_counter, 0, gasto['despesa'])
                worksheet.write(linha_counter, 1, gasto['valor'])
                worksheet.write(linha_counter, 2, gabinete)
                worksheet.write(linha_counter, 3, str(gasto['mes']) + '/' + str(gasto['ano']))
                linha_counter=linha_counter+1
            
            print('---------------------- fim de um gabinete ----------------------')

except:
    planilha.close()    

planilha.close()