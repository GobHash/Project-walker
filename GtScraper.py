# -*- coding: utf-8 -*-
"""
this Script is responsible for scrapping all Adjudications on guatecompras.gt
it starts at this page (http://guatecompras.gt/proveedores/consultaadvprovee.aspx)
and then it asks the user, which year they want to scrape
"""
import calendar
import datetime
import logging
import os
import re
import time
from math import ceil

import requests
from bs4 import BeautifulSoup

import load_assets

logging.basicConfig(filename='activity.log', level=logging.DEBUG)
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

FACTOR_ESPERA = 5 # segundos de espera antes de enviar el siguiente request, ver scrapeDay

TIMEOUT = 60 # segundos de espera antes de botar conexion con el server
HEADERS = requests.utils.default_headers()
HEADERS.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0'})
HEADERS.update({'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1'})
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
#estas lineas son para la carga de datos en masa
#para la version de carga diaria no se va a guardar info de manera local
#PROVEEDORES_LIST = load_assets.load_proveedores()
COMPRADORES_LIST = load_assets.load_compradores()
ADJUDICACIONES_DIARIAS = []
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
    req = requests.Request('GET', MAIN_URL, headers=HEADERS)
    prepped = SESSION.prepare_request(req)
    response = SESSION.send(prepped, timeout=TIMEOUT)
    if response.status_code != OK_CODE:
        logging.error('La request de la main URL fallida, error %s', response.status_code)
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
    response = SESSION.send(prepped, timeout=TIMEOUT)

    if response.status_code != OK_CODE:
        logging.error('error al iniciar, recibe el codigo %s, del server', response.status_code)
        return
    logging.debug('Ya tengo tengo el response (pag2.html) completado exitosamente')
    #es en este response en que ya estoy en un punto similar al de pag2.html
    #ahora toca ir pidiendo los dias
    contenido = response.content

    tokens = obtain_tokens(contenido)
    logging.debug('ya fueron actualizados los tokens para el siguiente request(POST) del mes %s', month)

    #creo el calendario para iterar sobre las fechas requeridas
    lista_dias = CALENDARIO.itermonthdates(year, int(month))


    #scrape_day(27,9,2016,tokens)
    #scrape_day(1,11,2016,tokens)
    #scrape_day(1, 1, 16, tokens)
    #return
    #
    mydf = open('ultimo_exito.txt', 'r')
    ultimo_exito = mydf.read().split(',')
    mydf.close()
    hay_min = False
    print ultimo_exito
    print 'ld'
    if len(ultimo_exito) > 1:
        min_dia = int(ultimo_exito[0])
        min_mes = int(ultimo_exito[1])
        min_year = int(ultimo_exito[2])
        hay_min = True
    for mi_dia in lista_dias:
        el_mes = str(mi_dia)[5:7]
        if el_mes == month:
            print mi_dia
            if hay_min:
                if int(year) >= min_year:
                    if int(month) >= min_mes:
                        if int(str(mi_dia)[8:]) > min_dia:
                            start2 = time.time()
                            scrape_day(str(mi_dia)[8:], month, year, tokens)
                            print 'It took {0:0.1f} seconds'.format(time.time() - start2)
                            load_assets.gen_csv(ADJUDICACIONES_DIARIAS, CAMPOS_ADJUDICACIONES, 'adjudicaciones/adjudicaciones.csv')
                            logging.info('agregadas al csv las adjs')
                            ADJUDICACIONES_DIARIAS = []
                            min_dia = int(str(mi_dia)[8:])
                            min_mes = int(month)
                            min_year = int(year)
                            mydf = open('ultimo_exito.txt', 'w')
                            min_date = '{},{},{}'.format(min_dia, min_mes, min_year)
                            mydf.write(min_date)
                            mydf.close()
                            logging.info('actualizado el archivo de fechas')
            else:
                start2 = time.time()
                scrape_day(str(mi_dia)[8:], month, year, tokens)
                print 'It took {0:0.1f} seconds'.format(time.time() - start2)
                load_assets.gen_csv(ADJUDICACIONES_DIARIAS, CAMPOS_ADJUDICACIONES, 'adjudicaciones/adjudicaciones.csv')
                logging.info('agregadas al csv las adjs')
                ADJUDICACIONES_DIARIAS = []
                min_dia = int(str(mi_dia)[8:])
                min_mes = int(month)
                min_year = int(year)
                hay_min = True
                mydf = open('ultimo_exito.txt', 'w')
                min_date = '{},{},{}'.format(min_dia, min_mes, min_year)
                mydf.write(min_date)
                mydf.close()
                logging.info('actualizado el archivo de fechas')
        #if i > 7:
            #break



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
    req = requests.Request('POST', MAIN_URL, headers=HEADERS, data=my_params)
    prepped = SESSION.prepare_request(req)
    response = SESSION.send(prepped, timeout=TIMEOUT)

    if response.status_code != OK_CODE:
        logging.error('Request fallida, codigo de respuesta: %s', response.status_code)
        raise ValueError('error al obtener el los datos del dia')

    logging.debug('Ya tengo tengo el response (pag3.html) completado exitosamente')

    contenido = response.content
    #se quita el caracter de la flecha que causa error al parsear
    contenido = contenido.replace('&#9660', '&#033')

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

    adjudicaciones_hoy = []
    proveedores_hoy = []
    compradores_hoy = []
    # hay que obtener la info de la primera pagina
    tabla = soup.findAll('tr', attrs={'class': re.compile('TablaFilaMix.')})
    for adjudicacion in tabla:
        #scrape_proveedor(adjudicacion.contents[2].find('a').get('href'))
        scrape_adjudicacion(adjudicacion.contents[5].find('a').get('href'))
        time.sleep(FACTOR_ESPERA)
        #scrape_adjudicacion()
        # link hacia la adj -> elem.contents[5].find('a').get('href')
        # nombre del proveedor -> elem.contents[2].find('a').string
        # NIT del proveedor -> elem.contents[3].string
        #print elem.contents[5].find('a').get('href'), elem.contents[2].find('a').string, elem.contents[3].string


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
        req = requests.Request('POST', MAIN_URL, headers=HEADERS, data=my_params)
        prepped = SESSION.prepare_request(req)
        response = SESSION.send(prepped, timeout=TIMEOUT)

        if response.status_code != OK_CODE:
            logging.error('Request fallida, codigo de respuesta: %s', response.status_code)
            raise ValueError('error al obtener la info del dia %s/%s/%s', day, month, year)


        logging.debug('obtenida la pag %s de %s', pag_actual, num_pags)

        if (pag_actual%10) == 1:
            new_tokens = obtain_tokens(contenido)
            my_params['__VIEWSTATE'] = new_tokens[0]
            my_params['__VIEWSTATEGENERATOR'] = new_tokens[1]
            my_params['__EVENTVALIDATION'] = new_tokens[2]

        contenido = contenido.replace('&#9660', '&#033')
        soup = BeautifulSoup(contenido, 'lxml')
        # ahora toca la parte de procesar la info que tienen las adjudicaciones
        tabla = soup.findAll('tr', attrs={'class': re.compile('TablaFilaMix.')})
        for adjudicacion in tabla:
            #scrape_proveedor(adjudicacion.contents[2].find('a').get('href'))
            scrape_adjudicacion(adjudicacion.contents[5].find('a').get('href'))
            time.sleep(FACTOR_ESPERA)

    logging.info('ya obtuve las adjudicaciones del dia')

    """
    mydf = open('dias.txt', 'a')
    VALORDIA = valor_d
    MAYORDIA = '{}/{}/{}'.format(day, month, year)
    mydf.write('{} - {}\n'.format(MAYORDIA, VALORDIA))
    mydf.close()
    """



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

def get_prov_adj(html, year):
    """poner doc
    """


    soup = BeautifulSoup(html, 'lxml')
    tabla = soup.findAll('tr', attrs={'class': re.compile('TablaFilaMix.')})
    totales = soup.find('span', attrs={'id': 'MasterGC_ContentBlockHolder_lblFilas'})
    init = totales.contents[0].index('de')
    fin = totales.contents[0].index('adjudicaciones')
    print int(totales.contents[0][init+2:fin].strip())

    print totales.contents
    for elem  in tabla:
        #print elem.contents
        """
        este es el modelo de cada fila de TAG que regresa guatecompras
        lo que nos interesa son el nombre y nit del proveedor para saber
        si hay que obtener su informacion o ya la obtuvimos anteriormente
        NOMBRE es elemento en posicion 2
        NIT es elemento en posicion 3
        [u'\n',
        <td align="left" style="width:10%;">19.feb..2016</td>,
        <td><a href="/proveedores/consultaDetProvee.aspx?rqp=4&amp;lprv=4397263" style="display:block" target="_blank"> INVERSIONES YOJUSA, SOCIEDAD ANONIMA</a></td>,
        <td align="left" style="width:10%;">66587727</td>,
        <td align="left" style="width:15%;">11,960.10</td>,
        <td align="left"><a href="/concursos/consultaDetalleCon.aspx?nog=4522540&amp;o=9">4522540</a></td>,
        u'\n']
        """

        # link hacia la adj -> elem.contents[5].find('a').get('href')
        # nombre del proveedor -> elem.contents[2].find('a').string
        # NIT del proveedor -> elem.contents[3].string
        #print elem.contents[5].find('a').get('href'), elem.contents[2].find('a').string, elem.contents[3].string
        pass

    #print tabla.find_all('a')
    #for ele in tabla:
        #print ele.get('a')
    #print tabla
    """
    #obtengo la tabla que tiene los resultados de los proveedores
    tabla = soup.find('table', attrs={'id': 'MasterGC_ContentBlockHolder_dgResultado'})
    proveedores = []
    links_proov = []
    for link in tabla.find_all('a'):
        if link.get('href').endswith(str(year)):
            #esto se hace para quitar el punto del inicio de la url
            tmp_url = link.get('href')[1:]
            links_proov.append(tmp_url)

    for row in tabla.findAll('tr', attrs={'class': 'TablaFila1'}):
        print row
    for row in tabla.findAll('tr', attrs={'class': 'TablaFila2'}):
        print row
    """
def scrape_adjudicacion(url):
    """
    metodo que recibe el numero de adjudicacion y se encarga de obtener
    la informacion que hay en su pagina
    """
    print url
    global COMPRADORES_LIST
    global ADJUDICACIONES_DIARIAS
    req = requests.Request('GET', '{}{}'.format(BASE_URL, url), headers=HEADERS)
    prepped = SESSION.prepare_request(req)
    response = SESSION.send(prepped, timeout=TIMEOUT)
    time.sleep(FACTOR_ESPERA/2.0)
    if response.status_code != OK_CODE:
        logging.error('Request fallida, codigo de respuesta: %s', response.status_code)
        raise ValueError('error la pagina de la adjudicacion %s', url)

    contenido = response.content
    """
    mydf = open('adjudicaciones/adj1.html', 'r')
    contenido = mydf.read()
    mydf.close()
    """
    contenido = contenido.replace('&#9660', '&#033')

    soup = BeautifulSoup(contenido, 'lxml')
    adjudicacion = {'nit_comprador':'',
                    'nit_proveedor':'',
                    'monto':'',
                    'unidades':'',
                    'fecha_adjudicada':'',
                    'fecha_publicada':'',
                    'modalidad_compra':'',
                    'categoria':''}

    #lleno primera la infor del comprador
    comprador = soup.find('span', attrs={'id': 'MasterGC_ContentBlockHolder_txtEntidad'})
    name_comprador = comprador.string.encode('utf-8')
    scrape_comprador(name_comprador, comprador.find('a').get('href'))
    adjudicacion['nit_comprador'] = COMPRADORES_LIST[name_comprador]['nit']

    tabla = soup.find('table', attrs={'id': 'MasterGC_ContentBlockHolder_dgProveedores'})
    #nit proveedor
    tag = tabla.find('tr', attrs={'class':'TablaFilaMix1'}).contents[1]
    adjudicacion['nit_proveedor'] = tag.string.encode('utf-8')
    # monto
    tag = tabla.find('tr', attrs={'class':'TablaFilaMix1'}).contents[4]
    adjudicacion['monto'] = tag.string.encode('utf-8')
    # fecha publicada
    tag = soup.find('span', attrs={'id': 'MasterGC_ContentBlockHolder_txtFechaPub'})
    adjudicacion['fecha_publicada'] = tag.string.encode('utf-8')
    # fecha finalizacion
    tag = soup.find('tr', attrs={'id': 'MasterGC_ContentBlockHolder_TrFechaFinalizacion'}).contents[3].find('span')
    adjudicacion['fecha_adjudicada'] = tag.string.encode('utf-8')
    # modalidad de compra
    tag = soup.find('span', attrs={'id': 'MasterGC_ContentBlockHolder_txtModalidad'})
    adjudicacion['modalidad_compra'] = tag.string.encode('utf-8')
    # categoria
    tag = soup.find('span', attrs={'id': 'MasterGC_ContentBlockHolder_txtCategoria'})
    if tag.string is None: # hay mas de una categoria
        cat = ''
        for i in range(len(tag.contents)):
            if i%2 == 0:
                cat += tag.contents[i].encode('utf-8') + '~'

        adjudicacion['categoria'] = cat[:-1]
    else:
        adjudicacion['categoria'] = tag.string.encode('utf-8')

    ADJUDICACIONES_DIARIAS.append(adjudicacion)

def scrape_comprador(nombre, url):
    """
    funcion que recibe el link hacia el comprador
    y luego guarda el objeto
    """
    global COMPRADORES_LIST

    if nombre in COMPRADORES_LIST:
        return
    cod = url[url.find('=')+1:url.find('&')]
    logging.info('obteniendo la info del comprador %s')
    # reviso si ya tengo la info del comprador de manera local

    # Al parecer no basta con tener la info de manera local
    # la info que tiene la adjudicacion del proveedor es el nombre


    if os.path.isfile('compradores/html/{}.html'.format(cod)):
        logging.debug('La informacion del comprador %s ya esta de manera local', cod)

    else:
        logging.debug('Se va a pedir al server la info del comprador %s', cod)

        req = requests.Request('GET', '{}{}'.format(BASE_URL, url), headers=HEADERS)
        prepped = SESSION.prepare_request(req)
        response = SESSION.send(prepped, timeout=TIMEOUT)
        time.sleep(FACTOR_ESPERA/2.0)
        if response.status_code != OK_CODE:
            logging.error('Request fallida, codigo de respuesta: %s', response.status_code)
            raise ValueError('error la pagina de la adjudicacion %s', url)

        contenido = response.content
        mydf = open('compradores/html/{}.html'.format(cod), 'w')
        mydf.writelines(contenido)
        mydf.close()
        # agregar a la lista
        comprador_actual = {'nit':'',
                            'tipo':'',
                            'nombre':'',
                            'origenFondos':'',
                            'departamento':'',
                            'municipio':''}
        
        soup = BeautifulSoup(contenido, 'lxml')
        # NIT
        comprador_actual['nit'] = soup.find('span', attrs={'id': 'MasterGC_ContentBlockHolder_Lbl_Nit'}).string.encode('utf-8')
        # tipo, se usa el next sibling 2 veces por que es el salto en los tr que hay que hacer
        comprador_actual['tipo'] = soup.find('tr', attrs={'id': 'MasterGC_ContentBlockHolder_trNit'}).next_sibling.next_sibling.contents[2].string.encode('utf-8')
        # nombre
        comprador_actual['nombre'] = soup.find('span', attrs={'id': 'MasterGC_ContentBlockHolder_lblEntidad'}).string.encode('utf-8')
        # origen de fondos
        if soup.find('span', attrs={'id': 'MasterGC_ContentBlockHolder_LblEntidadSiaf'}) is not None:
            comprador_actual['origenFondos'] = soup.find('span', attrs={'id': 'MasterGC_ContentBlockHolder_LblEntidadSiaf'}).string.encode('utf-8')
        # departamento
        comprador_actual['departamento'] = soup.find('span', attrs={'id': 'MasterGC_ContentBlockHolder_lblDepartamento'}).string.encode('utf-8')
        #municipio
        comprador_actual['municipio'] = soup.find('span', attrs={'id': 'MasterGC_ContentBlockHolder_lblMunicipio'}).string.encode('utf-8')

        COMPRADORES_LIST[comprador_actual['nombre']] = comprador_actual['nombre']



def scrape_proveedor(url):
    """
    funcion que obtiene los datos del proveedor y los agrega
    al CSV correspondiente
    :param url: link hacia el proveedor
    """
    cod = url[url.rfind('=')+1:]

    logging.info('voy a pedir la info del proveedor %s', cod)

    # reviso si ya tengo la info del proveedor de manera local
    if os.path.isfile('proveedores/html/{}.html'.format(cod)):
        logging.debug('La informacion del proveedor %s ya esta de manera local', cod)

    else:
        logging.debug('Se va a pedir al server la info del proveedor %s', cod)

        req = requests.Request('GET', '{}{}'.format(BASE_URL, url), headers=HEADERS)
        prepped = SESSION.prepare_request(req)
        response = SESSION.send(prepped, timeout=TIMEOUT)
        if response.status_code != OK_CODE:
            logging.error('Request fallida, codigo de respuesta: %s', response.status_code)
            raise ValueError('error la pagina de la adjudicacion %s', url)

        contenido = response.content
        soup = BeautifulSoup(contenido, 'lxml')
        mydf = open('proveedores/html/{}.html'.format(cod), 'w')
        mydf.writelines(contenido)
        mydf.close()


# 12 de mayo de 2016 ese dia hay mas de 500 adj
# lo que significa que se puede probar
# el algoritmo para paginacion con esos datos
#start = time.time()
#gen_csv_prov()
#load_assets.gen_csv_comp()
#scrape_month(2016, '02')
#print 'It took {0:0.1f} seconds'.format(time.time() - start)
#scrape_month(2016, '01')
#scrape_adjudicacion('nog=5230837&o=9')
#scrape_adjudicacion('/concursos/consultaDetalleCon.aspx?nog=4409809&o=9')
#print elht
#get_prov_adj(elht, 20)
#20/06/2016 - 551
#06/09/2016 - 623
#12/09/2016 - 675
#13/09/2016 - 637
#14/09/2016 - 659
#27/09/2016 - 811
