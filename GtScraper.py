# -*- coding: utf-8 -*-
"""
this Script is responsible for scrapping all Adjudications on guatecompras.gt
it starts at this page (http://guatecompras.gt/proveedores/consultaadvprovee.aspx)
and then it asks the user, which year they want to scrape
"""
import calendar
import csv
import datetime
import logging
import os
import re
import time
from math import ceil

import requests
from bs4 import BeautifulSoup

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
# no evite nuestras conexiones, se usa en el proceso de ScrapeDay
FACTOR_ESPERA = 1
#como su nombre lo indica, espera esa cantidad de segundos la respuesta del server antes de botar la conexion 
TIMEOUT = 15
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
    for mi_dia in lista_dias:
        el_mes = str(mi_dia)[5:7]
        if el_mes == month:
            print mi_dia
            #tokens = scrape_day(str(mi_dia)[8:], month, year, tokens)
            scrape_day(str(mi_dia)[8:], month, year, tokens)



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
    
    #mydf = open('main3.html', 'w')
    #mydf.writelines(response.content)
    #mydf.close()

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

        #mydf = open('subPag_{}.html'.format(pag_actual), 'w')
        #contenido = response.content
        #mydf.writelines(contenido)
        #mydf.close()


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
    req = requests.Request('GET', '{}{}'.format(BASE_URL, url), headers=HEADERS)
    prepped = SESSION.prepare_request(req)
    response = SESSION.send(prepped, timeout=TIMEOUT)
    if response.status_code != OK_CODE:
        logging.error('Request fallida, codigo de respuesta: %s', response.status_code)
        raise ValueError('error la pagina de la adjudicacion %s', url)
    val = len(response.content)
    contenido = response.content
    contenido = contenido.replace('&#9660', '&#033')
    soup = BeautifulSoup(contenido, 'lxml')
    comprador = soup.find('span', attrs={'id': 'MasterGC_ContentBlockHolder_txtEntidad'})
    print comprador.find('a').get('href')
    scrape_comprador(comprador.find('a').get('href'))
    #print soup.find('span', attrs={'id': 'MasterGC_ContentBlockHolder_txtTitulo'})

def scrape_comprador(url):
    """
    funcion que recibe el link hacia el comprador
    y luego guarda el objeto
    """
    cod = url[url.find('=')+1:url.find('&')]
    logging.info('obteniendo la info del comprador %s')
    # reviso si ya tengo la info del comprador de manera local
    if os.path.isfile('compradores/html/{}.html'.format(cod)):
        logging.debug('La informacion del comprador %s ya esta de manera local', cod)

    else:
        logging.debug('Se va a pedir al server la info del comprador %s', cod)

        req = requests.Request('GET', '{}{}'.format(BASE_URL, url), headers=HEADERS)
        prepped = SESSION.prepare_request(req)
        response = SESSION.send(prepped, timeout=TIMEOUT)
        if response.status_code != OK_CODE:
            logging.error('Request fallida, codigo de respuesta: %s', response.status_code)
            raise ValueError('error la pagina de la adjudicacion %s', url)

        contenido = response.content
        soup = BeautifulSoup(contenido, 'lxml')
        mydf = open('compradores/html/{}.html'.format(cod), 'w')
        mydf.writelines(contenido)
        mydf.close()

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




def gen_csv_prov():
    """
    genera el csv de los proveedores
    """
    provs = []
    campos = 'nit,tipo,nombre,fechaConstitucion,inscripcionRM,representanteLegal'
    provs.append(campos)
    for proveedor in os.listdir('proveedores/html/'):
        row = ''
        print proveedor
        #proveedor = '1256716.html'
        #proveedor = '1030082.html'
        #proveedor = '11.html'
        #proveedor = '530841.html'
        #proveedor = '57573.html'
        mydf = open('proveedores/html/{}'.format(proveedor), 'r')
        contenido = mydf.read()
        soup = BeautifulSoup(contenido, 'lxml')
        row += soup.find('span', attrs={'id': 'MasterGC_ContentBlockHolder_lblNIT'}).string + ','
        
        base = soup.find('div', attrs={'id': 'MasterGC_ContentBlockHolder_pnl_DatosInscripcion2'}).find('tr')
        # tipo
        tipo = base.contents[1].string
        row += tipo + ','
        # nombre
        row += soup.find('span', attrs={'id': 'MasterGC_ContentBlockHolder_lblNombreProv'}).string.replace(',,', ',', 1).replace(',', ' ') + ','
        if 'INDIVIDUAL' in tipo:
            # no hay
            # fecha de constitucion, repLegal, inscripcionRM
            row += ',,'
        else:
            base = soup.find('div', attrs={'id': 'MasterGC_ContentBlockHolder_pnl_DatosInscripcion2'}).find('tr')
            #print len(base.parent.find_all('tr'))
            # fecha de constitucion
            # entra a este caso no no hay fecha de constitucion (ver 11.html)
            if len(base.parent.find_all('tr')) < 3:
                row += ','
            else:
                row += base.next_sibling.next_sibling.contents[1].string + ','
            # fecha de inscripcion Registro Mercantil
            #cuando se cumple esta condicion, la empresa solo es provisional (ver 1030082.html)
            if len(base.parent.find_all('tr')) < 5:
                row += base.next_sibling.contents[1].string + ','
                #print '--'
            else:
                row += base.next_sibling.next_sibling.next_sibling.next_sibling.contents[1].string + ','
            # representante legal, se quita la ',,' entre nombres y apellidos
            if soup.find('a', attrs={'id': 'MasterGC_ContentBlockHolder_gvRepresentantesLegales_ctl02_proveedor'}) is None:
                row += ','
            else:
                rep_legal = soup.find('a', attrs={'id': 'MasterGC_ContentBlockHolder_gvRepresentantesLegales_ctl02_proveedor'}).next_sibling.string
                rep_legal = rep_legal.strip().replace(',,', ',', 1).replace(',', ' ')
                row += rep_legal
            #print '--'
        #break
        provs.append(row.encode('utf-8'))
        #break
        #print len(soup.find('table', attrs={'class': 'TablaForm3'}).contents)
        #print soup.find('table', attrs={'class': 'TablaForm3'}).table.find('td', attrs={'class': 'EtiquetaForm2'}).next_sibling.next_sibling
    
    with open('proveedores/object/proveedores.csv', 'w') as csvfile:
        for pr in provs:
            csvfile.write(pr+'\n')
    #soup = BeautifulSoup(contenido, 'lxml')
# 12 de mayo de 2016 ese dia hay mas de 500 adj
# lo que significa que se puede probar
# el algoritmo para paginacion con esos datos
gen_csv_prov()
#scrape_month(2016, '01')
#scrape_adjudicacion('nog=5230837&o=9')

#print elht
#get_prov_adj(elht, 20)
#20/06/2016 - 551
#06/09/2016 - 623
#12/09/2016 - 675
#13/09/2016 - 637
#14/09/2016 - 659
#27/09/2016 - 811
