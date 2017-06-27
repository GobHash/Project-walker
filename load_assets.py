"""
El proposito de este modulo es cargar la info de
compradores y proveedores en diccionarios para su uso.
Es importane notar que estas funciones(load_xxx) son solamente para ayudar
en la carga de data de cada anio.
Para la carga de datos diaria, estas funciones no van a ser necesarias.
Aqui tambien estan las funciones encargadas de generar los csv's
"""
import copy
import csv
import os

from bs4 import BeautifulSoup


def load_proveedores(proveedor_structure):
    """
    metodo encargado de llenar el diccionario
    de proveedores para que sea facil y rapido usar su info
    cuando se generan los csv's
    """
    print 'cargando info de proveedores'
    la_lista = {}
    campos = {'reps': []}
    for proveedor in os.listdir('proveedores/html/'):
        es_empresa = True
        proveedores = []
        proveedor_actual = proveedor_structure.copy()
        struc_actual = copy.deepcopy(campos)
        contenido = ''
        with open('proveedores/html/{}'.format(proveedor), 'r') as mydf:
            #print proveedor
            contenido = mydf.read()
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
                proveedores.append(proveedor_actual)    
        else:
            proveedores.append(proveedor_actual)
        for prov in proveedores:
            struc_actual['reps'].append(prov)
        la_lista[prov['nit']] = struc_actual
    print 'terminado de cargar informacion'
    return la_lista


def load_compradores(comprador_structure):
    """
    metodo encargado de llenar el diccionario
    de compradores para que sea facil y rapido usar su info
    cuando se generan los csv's
    """
    la_lista = {}
    print 'cargando info de compradores a memoria'
    for comprador in os.listdir('compradores/html/'):
        nueva_entidad = copy.deepcopy(comprador_structure)
        contenido = ''
        with open('compradores/html/{}'.format(comprador), 'r') as mydf:
            contenido = mydf.read()
        soup = BeautifulSoup(contenido, 'lxml')
        # nombre
        tag = soup.find('span', attrs={'id': 'MasterGC_ContentBlockHolder_lblEntidad'})
        entidad = obtain_tag_string(tag)
        # origen de fondos
        tag = soup.find('span', attrs={'id': 'MasterGC_ContentBlockHolder_LblEntidadSiaf'})
        if tag is not None:
            nueva_entidad['origen_fondos'] = obtain_tag_string(tag)

        la_lista[entidad] = nueva_entidad

    print 'terminados de cargar los compradores a memoria'
    return la_lista



def obtain_tag_string(tag):
    return tag.string.encode('utf-8').strip()

def gen_csv(adjudicaciones, campos, file, selector):
    with open(file, 'r') as mydf:
        contenido = mydf.read()
    try:
        with open(file, 'ab') as csvfile:
            fieldnames = campos
            writer = csv.DictWriter(csvfile,
                                    fieldnames=fieldnames,
                                    quotechar='|',
                                    quoting=csv.QUOTE_ALL)
            writer.writeheader()
            for adjudicacion in adjudicaciones:
                selector(adjudicacion, writer)
    except Exception as exp:
        with open(file, 'w') as mydf:
            mydf.write(contenido)
        raise exp
"""
def prov_writer(proveedor, writer):
    for rep in proveedor['reps']:
        writer.writerow(rep)

gen_csv(algo.values(), PROVEEDOR_BODY.keys(), 'proveedores/object/proveedores.csv', prov_writer)
"""
