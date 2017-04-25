# -*- coding: utf-8 -*-
"""
this Script is responsible for scrapping all Adjudications on guatecompras.gt
it starts at this page (http://www.guatecompras.gt/Proveedores/ConsultaProveeAdj.aspx)
and then it asks the user, which year they want to scrape
"""
import calendar
import datetime
from bs4 import BeautifulSoup
import requests


URL = 'http://www.guatecompras.gt/Proveedores/ConsultaProveeAdj.aspx'
BASE_URL_PROVEEDORES = "http://www.guatecompras.gt/Proveedores"
BASE_URL_COMPRADORES = "http://www.guatecompras.gt/compradores"
BASE_URL_ADJUDICACIONES = "http://www.guatecompras.gt/Concursos/consultaDetalleCon.aspx?"
ALGO = "http://www.guatecompras.gt/Proveedores/consultaDetProveeAdj.aspx?rqp=5&lprv=2068&iTipo=1&lper=2016"
MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
LOGFILE = "log.txt"
PENDIGFILE = "pending.txt"
OK_CODE = 200
HEADERS = requests.utils.default_headers()
HEADERS.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0'})
MAIN_URL = 'http://guatecompras.gt/proveedores/consultaadvprovee.aspx'
POST_PARAMS = {'MasterGC$ContentBlockHolder$ScriptManager1': '',
                   'MasterGC$ContentBlockHolder$rdbOpciones': '',
                   '__EVENTTARGET': '',
                   '__EVENTARGUMENT':'',
                   '__LASTFOCUS': '',
                   '__VIEWSTATE': '',
                   '__VIEWSTATEGENERATOR': '',
                   '__EVENTVALIDATION': ',
                   '__ASYNCPOST': 'true'}
#estos los params puestos en el body que son necesarios para poder moverme en la lista de
#proveedores adjudicados por año, que tiene como base -> URL




#esto sirve para que las cookies sean persistentes entre requests
SESSION = requests.Session()

def scrapedata():
    """
    this
    """
    continuar = raw_input("desea seguir con algun scrapping pendiente? (y/n)")
    now = datetime.datetime.now()
    log = ""
    if  continuar == 'y':
        log = "-------------------------------"
        log += "Log for completing previous run, started at: {}".format(now)
        #abrir el archivo que tiene la info de la sesion anterior y extraigo los datos necesarios
        #para seguir en el punto donde se queda
        fle = open(PENDIGFILE)
        fle.readlines()
        #ScrapeYear("")
    else:
        log = "-------------------------------"
        log += "Log for current run, started at: {}".format(now)
        year = raw_input("¿De que año desea obtener los datos de ajudicacion? (minimo 2004)\n")
        try:
            year = int(year)
            scrapeyear(year, log)
        except ValueError as err:
            print err.message


def scrapeyear(year, log):
    """
    este metodo es el encargado de obtener la info del año solicitado
    """

    #comienzo obteniendo la info de la pag base desde donde voy a buscar
    #se manda este primer request para obtener los tokens que el servidor
    #necesita para enviar el resto de la info de manera correcta
    #ver pag1.html 
    req = requests.Request('GET', MAIN_URL, headers=HEADERS)
    prepped = SESSION.prepare_request(req)
    response = SESSION.send(prepped)

    if response.status_code != OK_CODE:
        log += 'error al obtener url base este es el error obtenido {}'.format(response.status_code)
        raise ValueError('error al momento de obtener MAIN_URL, esta el codigo del response {}'.format(response.status_code))

    soup = BeautifulSoup(response.content, 'lxml')
    viewstate = soup.find('input', attrs={'id': '__VIEWSTATE'}).get('value')
    viewstate_gen = soup.find('input', attrs={'id': '__VIEWSTATEGENERATOR'}).get('value')
    event_val = soup.find('input', attrs={'id': '__EVENTVALIDATION'}).get('value')
    my_params = POST_PARAMS
    my_params['MasterGC$ContentBlockHolder$ScriptManager1'] = 'MasterGC$ContentBlockHolder$ScriptManager1|MasterGC$ContentBlockHolder$rdbOpciones$4'
    my_params['MasterGC$ContentBlockHolder$rdbOpciones'] = '5'
    my_params['__EVENTTARGET'] = 'MasterGC$ContentBlockHolder$rdbOpciones$4'
    my_params['__VIEWSTATE'] = viewstate
    my_params['__VIEWSTATEGENERATOR'] = viewstate_gen
    my_params['__EVENTVALIDATION'] = event_val

    #hay que revisar si es un mes específico, todo el año o solamente el día de hoy
    
    mes = 'todos'
    try:
        specific = raw_input('¿Ingrese el número del mes que desea obtener(1-12) ó 15 si es para todo el año?\n')
        specific = int(specific)
        if specific < 13 and specific > 0:
            mes = MESES[specific-1]
        elif specific < 16:
            pass
        else:
            mes = 'enero'
    except ValueError as err:
        print 'El valor ingresado no fue reconocido, por favor intente de nuevo'
        return
    
    #este request produce lo que esta en pag2.html
    #ya solamente falta definir las fechas que se quieren obtener
    #este response.content es la parte que genera pag2.html
    req = requests.Request('POST', MAIN_URL, headers=HEADERS, data=post_params)
    prepped = SESSION.prepare_request(req)
    response = SESSION.send(prepped)
    
    if response.status_code != OK_CODE:
        raise ValueError('error al obtener la pagina donde se filtra por fechas, el codigo de respuesta del servidor es el siguinte {}'.format(response.status_code))

    if mes == 'todos':
        #hacer el for aqui
        pass
    else:
        scrape_month(response, year, mes, log)
    
    
    """
    year_page = "{}{}{}".format(BASE_URL_PROVEEDORES, '/consultaProveeAdjLst.aspx?lper=', str(year))
    #genero el objeto de tipo request
    req = requests.Request('GET', year_page, headers=HEADERS)

    #ahora preparo el objeto request con los atributos del objeto SESSION
    prepped = SESSION.prepare_request(req)
    response = SESSION.send(prepped)

    if response.status_code != OK_CODE:
        log += "Error at request {}, got error: {}".format(req.headers, response.status_code)
        #terminar de escribir el log antes de salir
        return
    else:
        soup = BeautifulSoup(response.content, 'lxml')
        tabla = soup.find('table', attrs={'id': 'MasterGC_ContentBlockHolder_dgResultado'})
        pags = tabla.find('tr', attrs={'class': 'TablaPagineo'})
        print pags
        page_object = response.content
        #get_prov_adj(page_object, year)
    """

def scrape_month(first_page, year, month, log):
    """
    metodo encargado de iterar sobre el mes recibido en los params
    """
    soup = BeautifulSoup(first_page.content, 'lxml')
    mark1=contenido.index('|0|hiddenField|__EVENTTARGET|')
    mark2=contenido.index('|asyncPostBackControlIDs|')
    importante = contenido[mark1:mark2]
    el_contenedor = re.split(r'\|', importante)
    

def scrape_day(year, month, day, log):
    """
    metodo que se encargar de iterar sobre el dia del mes recibido en los params
    """
    pass
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


#scrapedata()


my_c = calendar.Calendar()
mc_ew = my_c.itermonthdates(2016,1)
for el in mc_ew:
    print el
print mc_ew