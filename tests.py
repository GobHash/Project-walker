"""
module solely made for testing purposes
"""

from bs4 import BeautifulSoup
import requests


URL = 'http://www.guatecompras.gt/Proveedores/ConsultaProveeAdj.aspx'
BASE_URL_PROVEEDORES = "http://www.guatecompras.gt/Proveedores"
BASE_URL_COMPRADORES = "http://www.guatecompras.gt/compradores"
BASE_URL_ADJUDICACIONES = "http://www.guatecompras.gt/Concursos/consultaDetalleCon.aspx?"
HEADERS = requests.utils.default_headers()
HEADERS.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0'})
SESSION = requests.Session()

def getyear():
    """asdfr
    """
    year = 2016
    year_page = "{}{}{}".format(BASE_URL_PROVEEDORES, '/consultaProveeAdjLst.aspx?lper=', str(year))
    req = requests.Request('GET', year_page, headers=HEADERS)
    prepped = SESSION.prepare_request(req)
    response = SESSION.send(prepped)
    mls = response.content
    soup = BeautifulSoup(mls, 'lxml')
    tabla = soup.find('table', attrs={'id': 'MasterGC_ContentBlockHolder_dgResultado'})


getyear()

def test2():
    req = requests.Request('GET', 'http://guatecompras.gt/proveedores/consultaadvprovee.aspx', headers=HEADERS)
    prepped = SESSION.prepare_request(req)
    response = SESSION.send(prepped)

    f = open("obtener-adjudicados-year.txt")
    req_body = f.read()
    f.close()
    req_body = req_body.format(2016, 2016)
    req = requests.Request('POST', 'http://guatecompras.gt/proveedores/consultaadvprovee.aspx', headers=HEADERS)
    prepped = SESSION.prepare_request(req)
    prepped.body = req_body
    response = SESSION.send(prepped)
    mkl = response.content
    soup = BeautifulSoup(mkl, "lxml")
    #print soup.prettify()


def voyhacer():
    """sdeqwe
    """

    response = SESSION.get(URL, headers=HEADERS)
    ml = response.content()
    soup = BeautifulSoup(ml, "lxml")
    tabla = soup.find('table', attrs={'class': 'Tabla1'})
    print tabla[1]

