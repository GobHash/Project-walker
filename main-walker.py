# -*- coding: utf-8 -*-
"""
this Script is responsible for scrapping all Adjudications on guatecompras.gt
it starts at this page (http://www.guatecompras.gt/Proveedores/ConsultaProveeAdj.aspx)
and then it asks the user, which year they want to scrape
"""
import calendar
import datetime
import logging
import re

import requests
from bs4 import BeautifulSoup

logging.basicConfig(filename='activity.log', level=logging.DEBUG)
CALENDARIO = calendar.Calendar()
MAIN_URL = 'http://guatecompras.gt/proveedores/consultaadvprovee.aspx'
BASE_URL_PROVEEDORES = "http://www.guatecompras.gt/Proveedores"
BASE_URL_COMPRADORES = "http://www.guatecompras.gt/compradores"
BASE_URL_ADJUDICACIONES = "http://www.guatecompras.gt/Concursos/consultaDetalleCon.aspx?"
MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
OK_CODE = 200
HEADERS = requests.utils.default_headers()
HEADERS.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0'})
POST_PARAMS = {'MasterGC$ContentBlockHolder$ScriptManager1': '',
               'MasterGC$ContentBlockHolder$rdbOpciones': '',
               '__EVENTTARGET': '',
               '__EVENTARGUMENT':'',
               '__LASTFOCUS': '',
               '__VIEWSTATE': '',
               '__VIEWSTATEGENERATOR': '',
               '__EVENTVALIDATION': '',
               '__ASYNCPOST': 'true'}
#esto sirve para que las cookies sean persistentes entre requests
SESSION = requests.Session()

def scrapedata():
    """
    this
    """
    continuar = raw_input("desea seguir con algun scrapping pendiente? (y/n)")
    now = datetime.datetime.now()
    logging.info('la corrida actual comienza el %s', str(now))
    log = ""
    if  continuar == 'y':
        log = "-------------------------------"
        log += "Log for completing previous run, started at: {}".format(now)
        #abrir el archivo que tiene la info de la sesion anterior y extraigo los datos necesarios
        #para seguir en el punto donde se queda
        fle = open('algo.txt')
        fle.readlines()
        #ScrapeYear("")
    else:
        log = "-------------------------------"
        log += "Log for current run, started at: {}".format(now)
        year = raw_input("¿De que año desea obtener los datos de ajudicacion? (minimo 2004)\n")
        try:
            year = int(year)
            scrapeyear(year, '01')
        except ValueError as err:
            print err.message


def scrapeyear(year, mes='15'):
    """
    este metodo es el encargado de obtener la info del año solicitado
    :param year: año que se va a obtener.
    :param log: log posiblemente se quite en version final.
    :param mes: el mes que se desea obtener, por defecto es 15 que significa todos los meses.
    """

    logging.info('Voy a obtener la info del año %s, en el mes %s', year, mes)
    if mes == '15':
        #hacer el for aqui
        pass
    else:
        scrape_month(year, mes)


def scrape_month(year, month):
    """
    metodo encargado de iterar sobre el mes recibido en los params
    :param year: año para obtener.
    :param mont: el mes en especifico que se quiere obtener.
    """
    #comienzo obteniendo la info de la pag base desde donde voy a buscar
    #se manda este primer request para obtener los tokens que el servidor
    #necesita para enviar el resto de la info de manera correcta
    #ver pag1.html
    req = requests.Request('GET', MAIN_URL, headers=HEADERS)
    prepped = SESSION.prepare_request(req)
    response = SESSION.send(prepped)
    logging.info('Voy a hacer el GET de la main URL (pag1.html) para el mes %s/%s', month, year)
    if response.status_code != OK_CODE:
        logging.error('La request de la main URL fue fallida, el codigo del server fue %s', response.status_code)
        return
    logging.debug('Requeste de la main URL completado exitosamente')

    soup = BeautifulSoup(response.content, 'lxml')
    #saco los atributos que me sirven para que el server me devuelva los datos correctos
    viewstate = soup.find('input', attrs={'id': '__VIEWSTATE'}).get('value')
    viewstate_gen = soup.find('input', attrs={'id': '__VIEWSTATEGENERATOR'}).get('value')
    event_val = soup.find('input', attrs={'id': '__EVENTVALIDATION'}).get('value')

    my_params = POST_PARAMS.copy()
    my_params['MasterGC$ContentBlockHolder$ScriptManager1'] = 'MasterGC$ContentBlockHolder$ScriptManager1|MasterGC$ContentBlockHolder$rdbOpciones$4'
    my_params['MasterGC$ContentBlockHolder$rdbOpciones'] = '5'
    my_params['__EVENTTARGET'] = 'MasterGC$ContentBlockHolder$rdbOpciones$4'
    my_params['__VIEWSTATE'] = viewstate
    my_params['__VIEWSTATEGENERATOR'] = viewstate_gen
    my_params['__EVENTVALIDATION'] = event_val

    logging.debug('Voy a hacer el request del primer POST del mes %s', month)
    req = requests.Request('POST', MAIN_URL, headers=HEADERS, data=my_params)
    prepped = SESSION.prepare_request(req)
    response = SESSION.send(prepped)
    
    if response.status_code != OK_CODE:
        logging.error('La request del primer POST recibe el codigo %s, del server', response.status_code)
        return
    logging.debug('Ya tengo tengo el response (pag2.html) completado exitosamente')
    #es en este response en que ya estoy en un punto similar al de pag2.html
    #ahora toca ir pidiendo los dias
    contenido = response.content

    #en el responde de la pag estos son los campos que delimitan la info que sirve
    mark1 = contenido.index('|0|hiddenField|__EVENTTARGET|')
    mark2 = contenido.index('|asyncPostBackControlIDs|')
    importante = contenido[mark1:mark2]
    el_contenedor = re.split(r'\|', importante)


    tokens = []
    tokens.append(el_contenedor[el_contenedor.index('__VIEWSTATE')+1])
    tokens.append(el_contenedor[el_contenedor.index('__VIEWSTATEGENERATOR')+1])
    tokens.append(el_contenedor[el_contenedor.index('__EVENTVALIDATION')+1])

    logging.debug('ya fueron actualizados los tokens para el siguiente request, POST, del mes %s', month)

    #creo el calendario para iterar sobre las fechas requeridas

    lista_dias = CALENDARIO.itermonthdates(year, int(month))
    for mi_dia in lista_dias:
        el_dia = str(mi_dia)[5:7]
        if el_dia == month:
            print mi_dia
            tokens = scrape_day(str(mi_dia)[8:], month, year, tokens)



def scrape_day(day, month, year, tokens):
    """
    metodo que se encargar de obtener la información de determinado día del mes
    """
    logging.info('voy a obtener la info para el %s/%s/%s', day, month, year)

    my_params = POST_PARAMS.copy()
    #vuelvo a actualizar los tokens que necesita el server
    #el uno(1) de abajo es porque buscamos proveedores con NIT
    my_params['MasterGC$ContentBlockHolder$txtFechaIni'] = '{}.{}.{}'.format(day, month, year)
    my_params['MasterGC$ContentBlockHolder$txtFechaFin'] = '{}.{}.{}'.format(day, month, year)
    my_params['MasterGC$ContentBlockHolder$txtMontoIni'] = ''
    my_params['MasterGC$ContentBlockHolder$txtMontoFin'] = ''
    my_params['MasterGC$ContentBlockHolder$ddlTipoProv'] = '1'
    my_params['MasterGC$ContentBlockHolder$Button1'] = 'Consultar'
    my_params['__VIEWSTATE'] = tokens[0]
    my_params['__VIEWSTATEGENERATOR'] = tokens[1]
    my_params['__EVENTVALIDATION'] = tokens[2]
    req = requests.Request('POST', MAIN_URL, headers=HEADERS, data=my_params)
    prepped = SESSION.prepare_request(req)
    response = SESSION.send(prepped)
    mydf = open('main3.html', 'w')
    mydf.writelines(response.content)
    mydf.close()
    if response.status_code != OK_CODE:
        logging.error('Request para los datos del %s/%s/%s fallida, codigo de respuesta del server: %s', day, month, year, response.status_code)
        raise ValueError('error al obtener el los datos del dia')

    logging.debug('Ya tengo tengo el response (pag3.html) completado exitosamente')
    contenido = response.content
    
    #actualizar los tokens para la siguiente ejecucion
    mark1 = contenido.index('|0|hiddenField|__EVENTTARGET|')
    mark2 = contenido.index('|asyncPostBackControlIDs|')
    importante = contenido[mark1:mark2]
    el_contenedor = re.split(r'\|', importante)
    tokens = []
    tokens.append(el_contenedor[el_contenedor.index('__VIEWSTATE')+1])
    tokens.append(el_contenedor[el_contenedor.index('__VIEWSTATEGENERATOR')+1])
    tokens.append(el_contenedor[el_contenedor.index('__EVENTVALIDATION')+1])
    logging.info('obtenida exitosamente la info para el %s/%s/%s', day, month, year)
    return tokens

def get_prov_adj(html, year):
    """poner doc
    """

    soup = BeautifulSoup(html, 'lxml')
    #obtengo la tabla que tiene los resultados de los proveedores
    tabla = soup.find('table', attrs={'id': 'MasterGC_ContentBlockHolder_dgResultado'})
    proveedores = []
    links_proov = []
    for link in tabla.find_all('a'):
        if link.get('href').endswith(str(year)):
            #esto se hace para quitar el punto del inicio de la url
            tmp_url = link.get('href')[1:]
            links_proov.append(tmp_url)
    
    
    """
    for row in tabla.findAll('tr', attrs={'class': 'TablaFila1'}):
        print row
    for row in tabla.findAll('tr', attrs={'class': 'TablaFila2'}):
        print row
    """
def scrape_adjudicacion():
    pass    



scrape_month(2016, '01')
