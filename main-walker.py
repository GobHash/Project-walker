# -*- coding: utf-8 -*-
"""
this Script is responsible for scrapping all Adjudications on guatecompras.gt
it starts at this page (http://www.guatecompras.gt/Proveedores/ConsultaProveeAdj.aspx)
and then it asks the user, which year they want to scrape
"""

import datetime
from bs4 import BeautifulSoup
import requests


URL = 'http://www.guatecompras.gt/Proveedores/ConsultaProveeAdj.aspx'
BASE_URL_PROVEEDORES = "http://www.guatecompras.gt/Proveedores"
BASE_URL_COMPRADORES = "http://www.guatecompras.gt/compradores"
BASE_URL_ADJUDICACIONES = "http://www.guatecompras.gt/Concursos/consultaDetalleCon.aspx?"
ALGO = "http://www.guatecompras.gt/Proveedores/consultaDetProveeAdj.aspx?rqp=5&lprv=2068&iTipo=1&lper=2016"
LOGFILE = "log.txt"
PENDIGFILE = "pending.txt"
HEADERS = requests.utils.default_headers()
HEADERS.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0'})

#estos los params puestos en el body que son necesarios para poder moverme en la lista de
#proveedores adjudicados por año, que tiene como base -> URL

BODY_PROVEEDOR = "MasterGC%24ContentBlockHolder%24ScriptManager1=MasterGC%24ContentBlockHolder%24UpdatePanel1%7CMasterGC%24ContentBlockHolder%24dgResultado%24ctl54%24ctl{}&MasterGC%24svrID=2&__EVENTTARGET=MasterGC%24ContentBlockHolder%24dgResultado%24ctl54%24ctl{}&__EVENTARGUMENT=&__VIEWSTATE=%2FwEPDwUKMTI4MzUzOTE3NA8WAh4CbFkC4A8WAmYPZBYCAgMPZBYCAgEPZBYCAgkPZBYCAgUPZBYCZg9kFgQCAw8WAh4EVGV4dAXNAjx0YWJsZSBjbGFzcz0iVGl0dWxvUGFnMSIgY2VsbFNwYWNpbmc9IjAiIGNlbGxQYWRkaW5nPSIyIiBhbGlnbj0iY2VudGVyIj48dHI%2BPHRkPjx0YWJsZSBjbGFzcz0iVGl0dWxvUGFnMiIgY2VsbFNwYWNpbmc9IjAiIGNlbGxQYWRkaW5nPSIyIj48dHI%2BPHRkIGNsYXNzPSJUaXR1bG9QYWczIiBhbGlnbj0iY2VudGVyIj48dGFibGUgY2xhc3M9IlRhYmxhRm9ybTMiIGNlbGxTcGFjaW5nPSIzIiBjZWxsUGFkZGluZz0iNCI%2BPHRyIGNsYXNzPSJFdGlxdWV0YUZvcm0yIj48dGQ%2BQcOxbzogMjAxNjwvdGQ%2BPC90cj48L3RhYmxlPjwvdGQ%2BPC90cj48L3RhYmxlPjwvdGQ%2BPC90cj48L3RhYmxlPmQCBw88KwALAQAPFgweC18hSXRlbUNvdW50AjIeCERhdGFLZXlzFgAeCVBhZ2VDb3VudAJuHhVfIURhdGFTb3VyY2VJdGVtQ291bnQC9yoeEFZpcnR1YWxJdGVtQ291bnQC9yoeEEN1cnJlbnRQYWdlSW5kZXgCCmRkZFguEZCnyNnGSjEQYXFIGKdKgyoi&__VIEWSTATEGENERATOR=9D9E12A9&__EVENTVALIDATION=%2FwEdAA9Ujf8tDdVR60xSxong3rEXDgb8Uag%2BidZmhp4z8foPgz4xN15UhY4K7pA9ni2czGCFp%2B0LzW2X25e7x6qJGAGNEDIBsVJcI17AvX4wvuIJ5AgMop%2Bg%2BrIcjfLnqU7sIEd1r49BNud9Gzhdq5Du6Cuaivj%2FJ0Sb6VUF9yYCq0O32nVzQBnAbvzxCHDPy%2FdQNW4JRFkop3STShyOPuu%2BQjyFyEKGLUzsAW%2FS22pN4CQ1k%2FPmspiPnyFdAbsK7K0ZtyIv%2Fuu03tEXAoLdp793x%2BCR9OyF7E4fiCuWyYf9%2Fub7OV4lSLlkj4PDQ33Ra1msgGvJjjHg8K2DXCSs%2Bek%2F5t9N4%2B%2FQ1A%3D%3D&__ASYNCPOST=true&"


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
        year = raw_input("¿De que anio desea obtener los datos de ajudicacion? (minimo 2004)\n")
        try:
            year = int(year)
            scrapeyear(year, log)
        except Exception:
            print "el año ingresado no fue reconocido"


def scrapeyear(year, log):
    """poner doc
    """
    year_page = "{}{}{}".format(BASE_URL_PROVEEDORES, '/consultaProveeAdjLst.aspx?lper=', str(year))
    #genero el objeto de tipo request
    req = requests.Request('GET', year_page, headers=HEADERS)

    #ahora preparo el objeto request con los atributos del objeto SESSION
    prepped = SESSION.prepare_request(req)
    response = SESSION.send(prepped)

    if response.status_code != 200:
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
scrapeyear(2016,"")


