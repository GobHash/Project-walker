# -*- coding: utf-8 -*-
"""
this Script is responsible for scrapping all Adjudications on guatecompras.gt
it starts at this page (http://guatecompras.gt/proveedores/consultaadvprovee.aspx)
and then it asks the user, which year they want to scrape
"""
import calendar
import copy
import datetime
import logging
from random import randint
import re
import time
from math import ceil, floor

import requests
import requests.exceptions as ex
from bs4 import BeautifulSoup

import load_assets

logging.basicConfig(filename='activity.log', level=logging.DEBUG)
logging.info('********************************nueva ejecucion del programa********************************')
CALENDARIO = calendar.Calendar()
MAIN_URL = 'http://guatecompras.gt/proveedores/consultaadvprovee.aspx'
BASE_URL = 'http://www.guatecompras.gt'
BASE_URL_PROVEEDORES = "http://www.guatecompras.gt"
BASE_URL_COMPRADORES = "http://www.guatecompras.gt/compradores"
BASE_URL_ADJUDICACIONES = "http://www.guatecompras.gt/Concursos/consultaDetalleCon.aspx?"
MESES = ['enero',
         'febrero',
         'marzo',
         'abril',
         'mayo',
         'junio',
         'julio',
         'agosto',
         'septiembre',
         'octubre',
         'noviembre',
         'diciembre']
OK_CODE = 200
# este numero de abajo es cuantos segundo se van a esperar entre request para que el servidor

FACTOR_ESPERA = 9 # segundos de espera antes de enviar el siguiente request, ver scrapeDay

TIMEOUT = 240 # segundos de espera antes de botar conexion con el server
HEADERS = requests.utils.default_headers()
USER_AGENTS = ['Mozilla/5.0 (Windows NT 10.0',
               'Mozilla/5.0 (iPad; CPU OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1',
               'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
               'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.111 Safari/537.36',
               'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
               'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.1 Safari/603.1.30',
               'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
               'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0) Gecko/20100101 Firefox/12.0',
               'Mozilla/5.0 (X11; U; Linux x86_64; de; rv:1.9.2.8) Gecko/20100723 Ubuntu/10.04 (lucid) Firefox/3.6.8',
               'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)']
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
CSV_ADJ = 'adjudicaciones/adj_csv.csv'
# estructura de la adjudicacion
ADJUDICACION_BODY = {'nog': '',
                     'categoria':'',
                     'descripcion':'',
                     'modalidad_compra':'',
                     'nit_comprador':'',
                     'nombre_comprador': '',
                     'fecha_publicada':'',
                     'fecha_presentacion_ofertas':'',
                     'fecha_cierre_ofertas':'',
                     'tipo_ofertas':'',
                     'fecha_adjudicada':'',
                     'status':'',
                     'unidades':'',
                     'nit_proveedor':'',
                     'monto':''}
# estructura del proveedor
PROVEEDOR_BODY = {'nit': 'null',
                  'municipio': 'null',
                  'departamento': 'null',
                  'nombre': 'null',
                  'rep_legal': 'null',
                  'activ_economica': 'null',
                  'tipo': 'null',
                  'inscripcion_rm': 'null'}
# la estructura de la unidad compradora (acceso a la info., conserjeria, ornato, etc.)
COMPRADOR_BODY = {'nit':'',
                  'nombre':'',
                  'departamento':'',
                  'municipio':'',
                  'entidad_superior': '',
                  'origen_fondos':'null'}
# la estructura de la entidad general (Ministerio de la defensa, IGSS, etc.)
TEMPLATE_COMPRADOR = {'unidades': {},
                      'origen_fondos':'null'}


#estas lineas son para la carga de datos en masa
#para la version de carga diaria no se va a guardar info de manera local
PROVEEDORES_LIST = {}#load_assets.load_proveedores(PROVEEDOR_BODY)
COMPRADORES_LIST = {}#load_assets.load_compradores(TEMPLATE_COMPRADOR)
ADJUDICACIONES_DIARIAS = {}
CAMPOS_ADJUDICACIONES = ['nit_comprador',
                         'nit_proveedor',
                         'monto',
                         'unidades',
                         'fecha_adjudicada',
                         'fecha_publicada',
                         'modalidad_compra',
                         'categoria']
#esto sirve para que las cookies sean persistentes entre requests
SESSION = requests.Session()

def cargar_compradores():
    """
    metodo encargado de poblar los compradores conocidos
    con la info local
    """
    global COMPRADORES_LIST
    COMPRADORES_LIST = load_assets.load_compradores(TEMPLATE_COMPRADOR)

def cargar_proveedores():
    """
    metodo encargado de poblar los proveedores conocidos
    con la info local
    """
    global PROVEEDORES_LIST
    PROVEEDORES_LIST = load_assets.load_proveedores(PROVEEDOR_BODY)

def scrapedata():
    """
    this
    """
    continuar = raw_input("desea seguir con algun scrapping pendiente? (y/n)")
    now = datetime.datetime.now()
    logging.info('la corrida actual comienza el %s', str(now))
    if  continuar == 'y':
        #abrir el archivo que tiene la info de la sesion anterior y extraigo los datos necesarios
        #para seguir en el punto donde se queda
        fle = open('algo.txt')
        fle.readlines()
        #ScrapeYear("")
    else:
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
    y generar los csv correspondientes
    :param year: año para obtener.
    :param month: el mes en especifico que se quiere obtener.
    """
    global ADJUDICACIONES_DIARIAS
    global CAMPOS_ADJUDICACIONES
    #comienzo obteniendo la info de la pag base desde donde voy a buscar
    #se manda este primer request para obtener los tokens que el servidor
    #necesita para enviar el resto de la info de manera correcta
    #ver pag1.html

    logging.info('Voy a hacer el GET de la main URL (pag1.html) para el  %s/%s', month, year)
    contenido = obtain_html_content('GET', MAIN_URL)

    logging.debug('Requeste de la main URL completado exitosamente')

    soup = BeautifulSoup(contenido, 'lxml')
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

    contenido = obtain_html_content('POST', MAIN_URL, data=my_params)
    tokens = obtain_tokens(contenido)

    logging.debug('ya fueron actualizados los tokens para el siguiente request(POST) del mes %s', month)

    lista_dias = CALENDARIO.itermonthdates(year, int(month))
    ultimo_exito = []
    with open('ultimo_exito.txt', 'r') as mydf:
        ultimo_exito = mydf.read().split(',')
    hay_min = False
    obtain_info = False
    print ultimo_exito
    if len(ultimo_exito) > 1:
        min_dia = int(ultimo_exito[0])
        min_mes = int(ultimo_exito[1])
        min_year = int(ultimo_exito[2])
        hay_min = True
    ind = 1
    for mi_dia in lista_dias:
        if ind > 3:
            break
        el_mes = str(mi_dia)[5:7]
        if el_mes == month: # hay dias que no son del mes actual, por el funcionamiento de las fechas en python
            print mi_dia
            #ind += 1
            if hay_min: # ya hay algun dia previo completado
                if int(year) < min_year: #si el anio es mayor se sacan datos, de lo contrario se
                    print 'la fecha solicitada({}/{}) es anterior a la ultima obtenida exitosamente'.format(str(mi_dia)[8:], month)
                    print 'edite el archivo ultimo_exito.txt para seguir adelante'
                    return

                if int(month) < min_mes: # datos de un mes anterior
                    print 'la fecha solicitada({}/{}) es anterior a la ultima obtenida exitosamente'.format(str(mi_dia)[8:], month)
                    print 'edite el archivo ultimo_exito.txt para seguir adelante'
                    return
                else: #si hay cambio de mes, entonces el dia va a cambiar
                    if int(month) > min_mes: # estoy en un mes posterior
                        obtain_info = True
                    elif int(str(mi_dia)[8:]) > min_dia: # mismo mes
                        obtain_info = True

            else: # no hay algun dia previo completado
                obtain_info = True

        if obtain_info:
            start2 = time.time()
            scrape_day(str(mi_dia)[8:], month, year, tokens)
            print 'It took {0:0.1f} seconds'.format(time.time() - start2)
            load_assets.gen_csv(ADJUDICACIONES_DIARIAS.values(),
                                ADJUDICACION_BODY.keys(),
                                'adjudicaciones/adjudicaciones.csv',
                                adj_writer)
            logging.info('agregadas al csv las adjs')
            ADJUDICACIONES_DIARIAS.clear()
            with open('ultimo_exito.txt', 'w') as mydf:
                min_date = '{},{},{}'.format(str(mi_dia)[8:], month, year)
                mydf.write(min_date)
                min_dia = int(str(mi_dia)[8:])
                min_mes = int(month)
                min_year = int(year)
                hay_min = True
                logging.info('actualizado el archivo de fechas')
            obtain_info = False

    load_assets.gen_csv(COMPRADORES_LIST.values(),
                        COMPRADOR_BODY.keys(),
                        'compradores/object/compradores.csv',
                        comp_writer)
    # activar esta parte para escribir los proveedores
    #load_assets.gen_csv(COMPRADORES_LIST, COMPRADOR_BODY.keys(), 'proveedores/object/proveedores.csv', prov_writer)

def scrape_day(day, month, year, tokens):
    """
    metodo que se encargar de obtener la información de determinado día del mes
    :param day: el dia que se quiere obtener. ej: 22
    :param month: el mes en especifico que se quiere obtener. ej: 5
    :param year: año para obtener. ej: 2016
    :param tokens: el viewstate y otros elementos requeridos, es un array
    """
    logging.info('voy a obtener la info para el %s/%s/%s', day, month, year)

    my_params = POST_PARAMS.copy()
    #vuelvo a actualizar los tokens que necesita el server
    my_params['MasterGC$ContentBlockHolder$txtFechaIni'] = '{}.{}.{}'.format(day, month, year)
    my_params['MasterGC$ContentBlockHolder$txtFechaFin'] = '{}.{}.{}'.format(day, month, year)
    my_params['MasterGC$ContentBlockHolder$txtMontoIni'] = ''
    my_params['MasterGC$ContentBlockHolder$txtMontoFin'] = ''
    #el uno(1) de abajo es porque buscamos proveedores con NIT
    my_params['MasterGC$ContentBlockHolder$ddlTipoProv'] = '1'
    my_params['MasterGC$ContentBlockHolder$Button1'] = 'Consultar'
    my_params['__VIEWSTATE'] = tokens[0]
    my_params['__VIEWSTATEGENERATOR'] = tokens[1]
    my_params['__EVENTVALIDATION'] = tokens[2]

    contenido = obtain_html_content('POST', MAIN_URL, data=my_params)

    soup = BeautifulSoup(contenido, 'lxml')

    # si no hay resultados este elemento no viene
    totales = soup.find('span', attrs={'id': 'MasterGC_ContentBlockHolder_lblFilas'})
    if totales is None:
        logging.info('No hay adjudicaciones para este dia')
        return

    init = totales.contents[0].index('de')
    fin = totales.contents[0].index('adjudicaciones')
    total_dia = int(totales.contents[0][init+2:fin].strip())
    num_pags = int(ceil(total_dia/50.))

    logging.info('Para este dia hay %s adjudicaciones', total_dia)

    # hay que obtener la info de la primera pagina
    tabla = soup.findAll('tr', attrs={'class': re.compile('TablaFilaMix.')})
    scrape_table(tabla)

    del my_params['MasterGC$ContentBlockHolder$Button1']
    new_tokens = obtain_tokens(contenido)
    my_params['__VIEWSTATE'] = new_tokens[0]
    my_params['__VIEWSTATEGENERATOR'] = new_tokens[1]
    my_params['__EVENTVALIDATION'] = new_tokens[2]

    # valores necesarios para calcular el numero de pag (relativo)
    offset = num_pags%10
    band = offset > 1

    # se arma el numero de pag que se necesita pedir
    for pag_actual in range(2, num_pags+1):
        # las primeras paginas si se piden con su numero al servidor
        if pag_actual < 12:
            if pag_actual < 10:
                my_params['MasterGC$ContentBlockHolder$ScriptManager1'] = 'MasterGC$ContentBlockHolder$UpdatePanel2|MasterGC$ContentBlockHolder$dgResultado$ctl54$ctl0{}'.format(pag_actual)
                my_params['__EVENTTARGET'] = 'MasterGC$ContentBlockHolder$dgResultado$ctl54$ctl0{}'.format(pag_actual)
            else:
                my_params['MasterGC$ContentBlockHolder$ScriptManager1'] = 'MasterGC$ContentBlockHolder$UpdatePanel2|MasterGC$ContentBlockHolder$dgResultado$ctl54$ctl{}'.format(pag_actual)
                my_params['__EVENTTARGET'] = 'MasterGC$ContentBlockHolder$dgResultado$ctl54$ctl{}'.format(pag_actual)
        else:
            la_pag = pag_actual
            # a partir de la 13va pagina el numero de pagina se vuelve relativo y se calcula
            # con la expresion de abajo
            if band:
                la_pag = la_pag - offset + 1

            if la_pag < 10:
                my_params['MasterGC$ContentBlockHolder$ScriptManager1'] = 'MasterGC$ContentBlockHolder$UpdatePanel2|MasterGC$ContentBlockHolder$dgResultado$ctl54$ctl0{}'.format(la_pag)
                my_params['__EVENTTARGET'] = 'MasterGC$ContentBlockHolder$dgResultado$ctl54$ctl0{}'.format(la_pag)
            else:
                my_params['MasterGC$ContentBlockHolder$ScriptManager1'] = 'MasterGC$ContentBlockHolder$UpdatePanel2|MasterGC$ContentBlockHolder$dgResultado$ctl54$ctl{}'.format(la_pag)
                my_params['__EVENTTARGET'] = 'MasterGC$ContentBlockHolder$dgResultado$ctl54$ctl{}'.format(la_pag)


        logging.debug('voy a pedir la pag %s', pag_actual)

        # pido la pag que necesito
        logging.debug('obtenida la pag %s de %s', pag_actual, num_pags)
        contenido = obtain_html_content('POST', MAIN_URL, data=my_params)
        if (pag_actual%10) == 1:
            new_tokens = obtain_tokens(contenido)
            my_params['__VIEWSTATE'] = new_tokens[0]
            my_params['__VIEWSTATEGENERATOR'] = new_tokens[1]
            my_params['__EVENTVALIDATION'] = new_tokens[2]


        soup = BeautifulSoup(contenido, 'lxml')
        # ahora toca la parte de procesar la info que tienen las adjudicaciones
        tabla = soup.findAll('tr', attrs={'class': re.compile('TablaFilaMix.')})
        scrape_table(tabla)

    logging.info('ya obtuve las adjudicaciones del dia')

    """
    mydf = open('dias.txt', 'a')
    VALORDIA = valor_d
    MAYORDIA = '{}/{}/{}'.format(day, month, year)
    mydf.write('{} - {}\n'.format(MAYORDIA, VALORDIA))
    mydf.close()
    """


def scrape_table(table):
    """
    metodo encargado de iterar sobre una tabla y obtener las adjudicaciones
    y los proveedores
    :param table: tabla que vamos a recorrer
    """
    # link hacia la adj -> elem.contents[5].find('a').get('href')
    # nombre del proveedor -> elem.contents[2].find('a').string
    # NIT del proveedor -> elem.contents[3].string
    #print elem.contents[5].find('a').get('href'), elem.contents[2].find('a').string, elem.contents[3].string
    for adjudicacion in table:
        #scrape_proveedor(elem.contents[3].string.strip(), adjudicacion.contents[2].find('a').get('href'))
        scrape_adjudicacion(obtain_tag_string(adjudicacion.contents[5].find('a')), adjudicacion.contents[5].find('a').get('href'))

def obtain_tokens(contenido):
    """
    metodo encargado de sacar los tokens que vienen
    en la respuesta del servidor
    :param contenido: es el html de la pag de la cual se quieren obtener los tokens
    :rtype list: la lista que tiene los tokens encontrados
    """
    #en el responde de la pag estos son los campos que delimitan la info que sirve
    mark1 = contenido.index('|0|hiddenField|__EVENTTARGET|')
    mark2 = contenido.index('|asyncPostBackControlIDs|')
    importante = contenido[mark1:mark2]
    el_contenedor = re.split(r'\|', importante)
    tokens = []
    tokens.append(el_contenedor[el_contenedor.index('__VIEWSTATE')+1])
    tokens.append(el_contenedor[el_contenedor.index('__VIEWSTATEGENERATOR')+1])
    tokens.append(el_contenedor[el_contenedor.index('__EVENTVALIDATION')+1])
    return tokens

def prov_writer(proveedor, writer):
    """
    metodo encargado de escribir la informacion
    del proveedor hacia el csv
    :param proveedor: lista que tiene los dicts de proveedor_body
    :param writer: el objeto que genera el csv
    """
    for rep in proveedor['reps']:
        writer.writerow(rep)
def comp_writer(comprador, writer):
    """
    metodo encargado de escribir la informacion
    del comprador hacia el csv
    :param comprador: lista que tiene los dicts de comprador_body
    :param writer: el objeto que genera el csv
    """
    for unidad in comprador['unidades']:
        writer.writerow(comprador['unidades'][unidad])

def adj_writer(adjudicaciones, writer):
    """
    metodo encargado de escribir la informacion
    de la adjudicacion hacia el csv
    :param proveedor: lista que tiene los dicts de adjudicacion_body
    :param writer: el objeto que genera el csv
    """
    for adjudicacion in adjudicaciones:
        writer.writerow(adjudicacion)
def scrape_adjudicacion(nog, url):
    """
    metodo que obtiene la informacion de la adjudicacion pedida
    :param nog: el NOG de guatecompras, para verificar si ya fue obtenida
    :param url: url hacia la adjudicacion
    """
    logging.debug(url)
    global COMPRADORES_LIST
    global ADJUDICACIONES_DIARIAS

    if nog in ADJUDICACIONES_DIARIAS:
        logging.info('informacion obtenida anteriormente')
        return
    logging.info('voy a pedir la info de una adjudicacion')
    contenido = obtain_html_content('GET', '{}{}'.format(BASE_URL, url))
    soup = BeautifulSoup(contenido, 'lxml')

    adjudicacion = ADJUDICACION_BODY.copy()
    adjudicaciones = []

    #lleno primera la info del comprador
    entidad_general = soup.find('span', attrs={'id': 'MasterGC_ContentBlockHolder_txtEntidad'})
    comprador = soup.find('span', attrs={'id': 'MasterGC_ContentBlockHolder_txtUE'})
    text1 = obtain_tag_string(entidad_general)
    text2 = obtain_tag_string(comprador)
    mi_comprador = scrape_comprador(text1,
                                    text2,
                                    comprador.find('a').get('href'))
    adjudicacion['nit_comprador'] = mi_comprador['nit']
    adjudicacion['nombre_comprador'] = mi_comprador['nombre']

    # nog
    tag = soup.find('span', attrs={'id': 'MasterGC_ContentBlockHolder_txtNOG'})
    adjudicacion['nog'] = obtain_tag_string(tag)
    # descripcion
    tag = soup.find('span', attrs={'id': 'MasterGC_ContentBlockHolder_txtTitulo'})
    adjudicacion['descripcion'] = obtain_tag_string(tag.contents[0])
    # estatus
    tag = soup.find('span', attrs={'id': 'MasterGC_ContentBlockHolder_txtEstatus'})
    adjudicacion['status'] = obtain_tag_string(tag)
    # unidades compradas (cantidad en la adjudicacion)

    if soup.find('table', attrs={'id': 'MasterGC_ContentBlockHolder_DgRubros'}) is None: # las adjudicaciones "normales"
        totales = soup.find('span', attrs={'id': 'MasterGC_ContentBlockHolder_lblFilas'})
        init = totales.contents[0].index('de')
        fin = totales.contents[0].index('tipos')
        total_dia = int(totales.contents[0][init+2:fin].strip())
        num_pags = int(ceil(total_dia/5.))
    else: # los contratos abiertos
        totales = soup.find('span', attrs={'id': 'MasterGC_ContentBlockHolder_lblFilasRubros'})
        init = totales.contents[0].index('de')
        fin = totales.contents[0].index('rubros')
        total_dia = int(totales.contents[0][init+2:fin].strip())
        num_pags = int(ceil(total_dia/5.))

    # DEBUG STATEMENT PARA EL PAGINADOR 
    if num_pags > 19:
        with open('paginas.txt', 'a') as mydf:
            mydf.write(url + '->')
            mydf.write(str(num_pags))
            mydf.write('----\n')
            return
    # valores necesarios para calcular el numero de pag (relativo)
    offset = num_pags%10
    band = offset > 1
    logging.debug('Se va a obtener la info para %s productos', total_dia)
    # los productos de la primera pagina
    acumulados = obter_cantidad_productos(soup)
    if total_dia > 5: # hay que pedir el resto de pags de los productos
        viewstate = soup.find('input', attrs={'id': '__VIEWSTATE'}).get('value')
        viewstate_gen = soup.find('input', attrs={'id': '__VIEWSTATEGENERATOR'}).get('value')
        event_val = soup.find('input', attrs={'id': '__EVENTVALIDATION'}).get('value')
        my_params = POST_PARAMS.copy()
        del my_params['MasterGC$ContentBlockHolder$rdbOpciones']
        my_params['__VIEWSTATE'] = viewstate
        my_params['__VIEWSTATEGENERATOR'] = viewstate_gen
        my_params['__EVENTVALIDATION'] = event_val
        my_params['MasterGC%24svrID'] = '4'
        my_params['MasterGC%24ContentBlockHolder%24cpe_ClientState'] = 'true'
        my_params['MasterGC%24ContentBlockHolder%24Cpe_oferente_ClientState'] = 'false'
        my_params['MasterGC%24ContentBlockHolder%24Cpe_Contrato_ClientState'] = 'true' if num_pags > 10 else ''
        for pag_actual in range(2, num_pags+1):
            #print pag_actual
            if pag_actual < 12:# los numeros de pagina son absolutos
                if pag_actual > 9:
                    my_params['MasterGC$ContentBlockHolder$ScriptManager1'] = 'MasterGC$ContentBlockHolder$PanelProductos|MasterGC$ContentBlockHolder$DGTipoProducto$ctl09$ctl{}'.format(pag_actual)
                    my_params['__EVENTTARGET'] = 'MasterGC$ContentBlockHolder$DGTipoProducto$ctl09$ctl{}'.format(pag_actual)
                else:
                    my_params['MasterGC$ContentBlockHolder$ScriptManager1'] = 'MasterGC$ContentBlockHolder$PanelProductos|MasterGC$ContentBlockHolder$DGTipoProducto$ctl09$ctl0{}'.format(pag_actual)
                    my_params['__EVENTTARGET'] = 'MasterGC$ContentBlockHolder$DGTipoProducto$ctl09$ctl0{}'.format(pag_actual)
            else:# los numeros de pagina son relativos
                la_pag = pag_actual
                # a partir de la 12va pagina el numero de pagina se vuelve relativo y se calcula
                # con la expresion de abajo
                if band:
                    la_pag = pag_actual - offset + 1
                #print la_pag
                if la_pag > 9:
                    my_params['MasterGC$ContentBlockHolder$ScriptManager1'] = 'MasterGC$ContentBlockHolder$PanelProductos|MasterGC$ContentBlockHolder$DGTipoProducto$ctl09$ctl{}'.format(la_pag)
                    my_params['__EVENTTARGET'] = 'MasterGC$ContentBlockHolder$DGTipoProducto$ctl09$ctl{}'.format(la_pag)
                else:
                    my_params['MasterGC$ContentBlockHolder$ScriptManager1'] = 'MasterGC$ContentBlockHolder$PanelProductos|MasterGC$ContentBlockHolder$DGTipoProducto$ctl09$ctl0{}'.format(la_pag)
                    my_params['__EVENTTARGET'] = 'MasterGC$ContentBlockHolder$DGTipoProducto$ctl09$ctl0{}'.format(la_pag)
            content = obtain_html_content('POST', '{}{}'.format(BASE_URL, url), data=my_params)
            if (pag_actual%10) == 1:
                new_tokens = obtain_tokens(content)
                my_params['__VIEWSTATE'] = new_tokens[0]
                my_params['__VIEWSTATEGENERATOR'] = new_tokens[1]
                my_params['__EVENTVALIDATION'] = new_tokens[2]
            acumulados += obter_cantidad_productos(BeautifulSoup(content, 'lxml'))
    acumulados = acumulados[:-1] # quitar el ~ del final
    adjudicacion['unidades'] = acumulados
    # fecha publicada
    tag = soup.find('span', attrs={'id': 'MasterGC_ContentBlockHolder_txtFechaPub'})
    adjudicacion['fecha_publicada'] = obtain_tag_string(tag)
    # fecha de presetacion ofertas
    tag = soup.find('span', attrs={'id': 'MasterGC_ContentBlockHolder_txtFechaPresentacion'})
    adjudicacion['fecha_presentacion_ofertas'] = obtain_tag_string(tag)
    # fecha de cierre de ofertas
    tag = soup.find('span', attrs={'id': 'MasterGC_ContentBlockHolder_txtFechacierreRecep'})
    adjudicacion['fecha_cierre_ofertas'] = obtain_tag_string(tag)
    # fecha de cierre de ofertas
    tag = soup.find('span', attrs={'id': 'MasterGC_ContentBlockHolder_txtFechacierreRecep'})
    adjudicacion['fecha_cierre_ofertas'] = obtain_tag_string(tag)
    # fecha de adjudicacion
    tag = soup.find('span', attrs={'id': 'MasterGC_ContentBlockHolder_txtFechaFinalización'})
    adjudicacion['fecha_adjudicada'] = obtain_tag_string(tag)
    # tipo de ofertas
    tag = soup.find('span', attrs={'id': 'MasterGC_ContentBlockHolder_txtRecepcionOferta'}).find('b')
    adjudicacion['tipo_ofertas'] = obtain_tag_string(tag)
    # modalidad de compra
    tag = soup.find('span', attrs={'id': 'MasterGC_ContentBlockHolder_txtModalidad'})
    adjudicacion['modalidad_compra'] = obtain_tag_string(tag)
    # categoria
    tag = soup.find('span', attrs={'id': 'MasterGC_ContentBlockHolder_txtCategoria'})
    if tag.string is None: # hay mas de una categoria
        cat = ''
        for i in range(len(tag.contents)):
            if i%2 == 0:
                cat += tag.contents[i].encode('utf-8') + '~'

        adjudicacion['categoria'] = cat[:-1]
    else:
        adjudicacion['categoria'] = obtain_tag_string(tag)

    # este objeto tiene la informacion de el(los) proveedor ajdudicados
    tabla = soup.find('table', attrs={'id': 'MasterGC_ContentBlockHolder_dgProveedores'})
    proveedores_adjudicados = tabla.findAll('tr', attrs={'class': re.compile('TablaFilaMix.')})
    for proveedor in proveedores_adjudicados:
        nueva_adj = adjudicacion.copy()
        #nit proveedor
        tag = proveedor.contents[1]
        nueva_adj['nit_proveedor'] = obtain_tag_string(tag)
        # monto
        tag = proveedor.contents[4]
        nueva_adj['monto'] = obtain_tag_string(tag)
        adjudicaciones.append(nueva_adj)

    ADJUDICACIONES_DIARIAS[nog] = adjudicaciones


def obter_cantidad_productos(soup):
    """
    metodo que devuelve el numero de productos en una pagina
    concatenados por '~'
    :param soup: objeto que tiene cargada la info de la pagina
    :rtype string: string que tiene las cantidades encontradas
    """
    holder = ''
    #print soup.find('tr', attrs={'class': 'TablaPagineo'})
    # este es para los contratos abiertos
    tag = soup.find('table', attrs={'id': 'MasterGC_ContentBlockHolder_DgRubros'})
    if tag is not None:
        tabla = tag.findAll('tr', attrs={'class': re.compile('TablaFila.')})
        for element in tabla:
            holder += obtain_tag_string(element.find('a')).strip() + '~'

    else: # este es para las adjudicaciones "normales"
        tag = soup.find('table', attrs={'id': 'MasterGC_ContentBlockHolder_DGTipoProducto'})
        tabla = tag.findAll('tr', attrs={'class': re.compile('TablaFilaMix.')})
        for i in range(len(tabla)):
            if i+3 < 10:
                cant = tabla[i].find('span', attrs={'id': 'MasterGC_ContentBlockHolder_DGTipoProducto_ctl0{}_lblcant'.format(i+3)})
            else:
                cant = tabla[i].find('span', attrs={'id': 'MasterGC_ContentBlockHolder_DGTipoProducto_ctl{}_lblcant'.format(i+3)})
                #                                         'MasterGC_ContentBlockHolder_DGTipoProducto_ctl03_lblcant'
            #print cant
            if cant is not None:
                holder += obtain_tag_string(cant) + '~'
    return holder

def scrape_comprador(entidad, unidad_compradora, url):
    """
    metodo encargado obtener la info de un comprador
    y devolver el un diccionario con comprador_body
    :param entidad: nombre de la entidad superior
    :param unidad_compradora: nombre de la unidad que buscamos
    :param url: link hacia la pag de la unidad compradora
    :rtype dict: diccionario de comprador_body
    """
    global COMPRADORES_LIST

    # reviso si ya tengo la info del comprador de manera local
    #algo = COMPRADORES_LIST[entidad]
    #print COMPRADORES_LIST[entidad]['unidades']
    obtener_origen_fondos = True
    if entidad in COMPRADORES_LIST:
        if unidad_compradora in COMPRADORES_LIST[entidad]['unidades']:
            return COMPRADORES_LIST[entidad]['unidades'][unidad_compradora]
        else:
            obtener_origen_fondos = False

    if url.startswith('/'):
        url = '{}{}'.format(BASE_URL, url)

    logging.info('obteniendo la info del comprador %s -> %s', unidad_compradora, entidad)

    contenido = obtain_html_content('GET', url)
    comprador_actual = COMPRADOR_BODY.copy()
    soup = BeautifulSoup(contenido, 'lxml')

    # NIT
    tag = soup.find('span', attrs={'id': 'MasterGC_ContentBlockHolder_Lbl_Nit'})
    cnt = 0
    while tag.string is None: # fix pirata xq es comun que truene en este elemento
        logging.error('el tag del NIT venia vacio')
        if cnt > 100:
            raise ValueError('ERROR AL TRATAR DE CONSEGUIR EL NIT')
        contenido = obtain_html_content('GET', url)
        soup = BeautifulSoup(contenido, 'lxml')
        tag = soup.find('span', attrs={'id': 'MasterGC_ContentBlockHolder_Lbl_Nit'})
        cnt += 1
    #print tag
    comprador_actual['nit'] = obtain_tag_string(tag)
    # nombre de la unidad compradora
    tag = soup.find('tr', attrs={'id': 'MasterGC_ContentBlockHolder_trNit'}).next_sibling.next_sibling.contents[2]
    comprador_actual['nombre'] = obtain_tag_string(tag)
    # departamento
    tag = soup.find('span', attrs={'id': 'MasterGC_ContentBlockHolder_lblDepartamento'})
    comprador_actual['departamento'] = obtain_tag_string(tag)
    #municipio
    tag = soup.find('span', attrs={'id': 'MasterGC_ContentBlockHolder_lblMunicipio'})
    comprador_actual['municipio'] = obtain_tag_string(tag)
    # entidad de la cual es parte la unidad compradora
    comprador_actual['entidad_superior'] = entidad

    if obtener_origen_fondos:
        tag = soup.find('span', attrs={'id': 'MasterGC_BarraNav'})
        link = tag.contents[8].get('href')
        contenido = obtain_html_content('GET', link)
        #contenido = response.content
        soup = BeautifulSoup(contenido, 'lxml')
        nueva_entidad = copy.deepcopy(TEMPLATE_COMPRADOR)
        tag = soup.find('span', attrs={'id': 'MasterGC_ContentBlockHolder_LblEntidadSiaf'})
        if tag is not None:
            nueva_entidad['origen_fondos'] = obtain_tag_string(tag)
            comprador_actual['origen_fondos'] = obtain_tag_string(tag)
        COMPRADORES_LIST[entidad] = nueva_entidad
    else:
        comprador_actual['origen_fondos'] = COMPRADORES_LIST[entidad]['origen_fondos']


    COMPRADORES_LIST[entidad]['unidades'][unidad_compradora] = comprador_actual
    return comprador_actual


def obtain_tag_string(tag):
    """
    metodo encargado de obtener el string de una etiqueta html
    :param tag: la etiqueta de la que vamos a extraer el texto
    :rtype string: string que representa lo encontrado
    """
    return tag.string.encode('utf-8').strip()


def obtain_html_content(request_type, url, data=None):
    """
    metodo encargado de realizar el request hacia la pag solicitada
    es capaz de volver a pedir la pag si la conexion falla o esperar
    si es que se sobrecarga al servidor destino
    :param request_type: si es un POST, GET, etc.
    :param url: link que vamos a consultar
    :param data: payload que se envia con el request
    :rtype string: que tiene el resultado
    """
    continuar = True
    resp = ''
    espera = FACTOR_ESPERA #segundos de espera inicial
    treshold = FACTOR_ESPERA*20
    max_ciclos = 1000
    ciclo_actual = 1
    while continuar and ciclo_actual <= max_ciclos:
        try:
            HEADERS['User-Agent'] = USER_AGENTS[randint(0, len(USER_AGENTS)-1)]
            req = requests.Request(request_type, url, headers=HEADERS, data=data)
            prepped = SESSION.prepare_request(req)
            response = SESSION.send(prepped, timeout=TIMEOUT)
            if response.status_code == OK_CODE:
                resp = response
                continuar = False
                # activarlo si comienzan a bloquear muy frecuentemente
                time.sleep(1) # espera 2 segundos para evitar cargar el server con el siguiente
            else: # hay que volver a pedir la info al server
                ciclo_actual += 1

        except (ex.ConnectTimeout, ex.ChunkedEncodingError, ex.ConnectionError) as la_exception:
            logging.exception(la_exception.message)
            logging.exception('voy a esperar %s seg', espera)
            time.sleep(espera)
            espera = ceil(espera*1.5)
            if espera > treshold:
                espera = ceil(espera/randint(1, 6))
                treshold = randint(floor(treshold*3/4), floor(treshold*7/5))
            ciclo_actual += 1
    #se quita el caracter de la flecha que causa error al parsear
    return resp.content.replace('&#9660', '&#033')

def scrape_proveedor(nit, url):
    """
    metodo encargado de obtener la informacion
    del proveedor solicitado y agrega un dict
    de proveedor_body a la lista de proveedores
    :param nit: NIT del proveedor
    :param url: link hacia el proveedor
    """
    global PROVEEDORES_LIST

    if nit in PROVEEDORES_LIST:
        return

    es_empresa = True
    logging.info('voy a pedir la info del proveedor %s', nit)

    proveedor_actual = PROVEEDOR_BODY.copy()
    proveedores = []
    campos = {'reps': []}
    contenido = obtain_html_content('GET', '{}{}'.format(BASE_URL, url))
    soup = BeautifulSoup(contenido, 'lxml')

    #nit
    tag = soup.find('span', attrs={'id': 'MasterGC_ContentBlockHolder_lblNIT'})
    proveedor_actual['nit'] = obtain_tag_string(tag)
    # nombre
    tag = soup.find('span', attrs={'id': 'MasterGC_ContentBlockHolder_lblNombreProv'})
    proveedor_actual['nombre'] = obtain_tag_string(tag)

    base = soup.find('div', attrs={'id': 'MasterGC_ContentBlockHolder_pnl_DatosInscripcion2'}).find('tr')
    # tipo
    for row in base.parent.findAll('tr'):
        row_info = obtain_tag_string(row.contents[0])
        if 'Tipo' in row_info:
            if 'INDIVIDUAL' in row.contents[1]: # las personas individuales no tienen datos de direccion
                es_empresa = False
            proveedor_actual['tipo'] = obtain_tag_string(row.contents[1])
        elif 'PROVISIONAL' in row_info:
            proveedor_actual['inscripcion_rm'] = obtain_tag_string(row.contents[1])
        elif 'DEFINITIVA' in row_info:
            proveedor_actual['inscripcion_rm'] = obtain_tag_string(row.contents[1])
        elif 'Actividad' in row_info:
            proveedor_actual['activ_economica'] = obtain_tag_string(row.contents[1])

    """
    Es importante resaltar que estas direcciones son obtenidas del domicilio fiscal,
    esto se debe a que no todas las empresas tiene registrado domicilio comercial (11.html).
    TO-DO: revisar si existe domicilio comercial y obtener esa info
    """
    if es_empresa:
        base = soup.find('div', attrs={'id': 'MasterGC_ContentBlockHolder_pnl_domicilioFiscal2'})
        for row in base.findAll('tr'):
            row_info = obtain_tag_string(row.contents[0])
            if 'Departamento' in row_info:
                proveedor_actual['departamento'] = obtain_tag_string(row.contents[1])
            elif 'Municipio' in row_info:
                proveedor_actual['municipio'] = obtain_tag_string(row.contents[1])
        # representantes legales
        tag = soup.find('a', attrs={'id': 'MasterGC_ContentBlockHolder_gvRepresentantesLegales_ctl02_proveedor'})
        if tag is not None:
            tabla = soup.find('table', attrs={'id': 'MasterGC_ContentBlockHolder_gvRepresentantesLegales'})
            for rep in tabla.findAll('tr', attrs={'class': 'FilaTablaDetalle'}):
                nuevo_prov = proveedor_actual.copy()
                nit = rep.find('a')
                tag = nit.next_sibling
                nuevo_prov['rep_legal'] = '{} {}'.format(obtain_tag_string(nit),
                                                         obtain_tag_string(tag).strip())
                proveedores.append(nuevo_prov)
        else:
            proveedores.append(nuevo_prov)
    else:
        proveedores.append(nuevo_prov)

    for prov in proveedores:
        campos['reps'].append(prov)
    PROVEEDORES_LIST[proveedor_actual['nit']] = campos


# 12 de mayo de 2016 ese dia hay mas de 500 adj
# lo que significa que se puede probar
# el algoritmo para paginacion con esos datos
#start = time.time()
#gen_csv_prov()
#load_assets.gen_csv_comp()
#scrape_month(2016, '02')
#print 'It took {0:0.1f} seconds'.format(time.time() - start)
#scrape_month(2016, '02')
#scrape_adjudicacion('/concursos/consultaDetalleCon.aspx?nog=4447441&o=9')
#scrape_comprador('HOSPITAL DE SAN BENITO', 'MINISTERIO DE SALUD PÚBLICA','/compradores/consultaDetEnt.aspx?iUnt2=76&iEnt=9&iUnt=0&iTipo=4')
#scrape_adjudicacion('/concursos/consultaDetalleCon.aspx?nog=4380401&o=9') # 109 tipos distintos de productos
#scrape_adjudicacion('/concursos/consultaDetalleCon.aspx?nog=4443454&o=9') # error en la obtencio del nit
#scrape_adjudicacion('/concursos/consultaDetalleCon.aspx?nog=4423550&o=9')
#scrape_adjudicacion('/concursos/consultaDetalleCon.aspx?nog=1148753&o=9') # adjudicacion de contrato abierto
#scrape_adjudicacion(12, '/concursos/consultaDetalleCon.aspx?nog=4409892&o=9') # 1.1.16 un proveedor varios productos
#load_assets.gen_csv(ADJUDICACIONES_DIARIAS.values(), ADJUDICACION_BODY.keys(), 'adjudicaciones/adjudicaciones3.csv', adj_writer)
#scrape_adjudicacion('/concursos/consultaDetalleCon.aspx?nog=6079695&o=9') # multiples proveedores y varios productos
#scrape_adjudicacion('/concursos/consultaDetalleCon.aspx?nog=4391691&o=9')
#scrape_adjudicacion('/concursos/consultaDetalleCon.aspx?nog=4423550&o=9') # 10 pags de productos
#scrape_proveedor('12', 'sadf')
#scrape_comprador('IGSS - ...', 'UNIDAD DE CONSULTA EXTERNA DE ENFERMEDADES', 'sf')
#scrape_comprador('MINDEF', 'ALGOPASA', 'sf')
#scrape_adjudicacion('/concursos/consultaDetalleCon.aspx?nog=4409809&o=9')
#print elht
#get_prov_adj(elht, 20)
#scrape_proveedor('12', 'sfas')
#load_assets.gen_csv([], ADJUDICACION_BODY.keys(), 'adjudicaciones/adjudicaciones.csv')
#20/06/2016 - 551
#06/09/2016 - 623
#12/09/2016 - 675
#13/09/2016 - 637
#14/09/2016 - 659
#27/09/2016 - 811
