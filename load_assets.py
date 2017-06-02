"""
El proposito de este modulo es cargar la info de
compradores y proveedores en diccionarios para su uso.
Es importane notar que estas funciones(load_xxx) son solamente para ayudar
en la carga de data de cada anio.
Para la carga de datos diaria, estas funciones no van a ser necesarias.
Aqui tambien estan las funciones encargadas de generar los csv's
"""
import csv
import os

from bs4 import BeautifulSoup


def load_proveedores():
    """
    metodo encargado de llenar el diccionario
    de proveedores para que sea facil y rapido usar su info
    cuando se generan los csv's
    """
    la_lista = {}
    for proveedor in os.listdir('proveedores/html/'):
        proveedor_actual = {'nit':'',
                            'tipo':'',
                            'nombre':'',
                            'fecha_constitucion':'',
                            'inscripcion_rm':'',
                            'representante_legal':''}
        contenido = ''
        with open('proveedores/html/{}'.format(proveedor), 'r') as mydf:
            contenido = mydf.read()
        soup = BeautifulSoup(contenido, 'lxml')
        #nit
        tag = soup.find('span', attrs={'id': 'MasterGC_ContentBlockHolder_lblNIT'})
        proveedor_actual['nit'] = tag.string.encode('utf-8')

        base = soup.find('div', attrs={'id': 'MasterGC_ContentBlockHolder_pnl_DatosInscripcion2'}).find('tr')
        # tipo
        tipo = base.contents[1].string
        proveedor_actual['tipo'] = tipo.encode('utf-8')
        #row.append(tipo.replace(',','').encode('utf-8'))
        # nombre
        tag = soup.find('span', attrs={'id': 'MasterGC_ContentBlockHolder_lblNombreProv'})
        proveedor_actual['nombre'] = tag.string.encode('utf-8')
        #soup.find('span', attrs={'id': 'MasterGC_ContentBlockHolder_lblNombreProv'}).string.replace(',,', ' ', 1).replace(',', ' ').encode('utf-8')
        if 'INDIVIDUAL' in tipo:
            pass
        else:
            base = soup.find('div', attrs={'id': 'MasterGC_ContentBlockHolder_pnl_DatosInscripcion2'}).find('tr')
            #print len(base.parent.find_all('tr'))
            # fecha de constitucion
            # entra a este caso no no hay fecha de constitucion (ver 11.html)
            if len(base.parent.find_all('tr')) < 3:
                pass
            else:
                tag = base.next_sibling.next_sibling.contents[1]
                proveedor_actual['fecha_constitucion'] = tag.string.encode('utf-8')
            # fecha de inscripcion Registro Mercantil
            #cuando se cumple esta condicion, la empresa solo es provisional (ver 1030082.html)
            if len(base.parent.find_all('tr')) < 5:
                tag = base.next_sibling.contents[1]
                proveedor_actual['inscripcion_rm'] = tag.string.encode('utf-8')
            else:
                tag = base.next_sibling.next_sibling.next_sibling.next_sibling.contents[1]
                proveedor_actual['inscripcion_rm'] = tag.string.encode('utf-8')
            # representante legal, se quita la ',,' entre nombres y apellidos
            if soup.find('a', attrs={'id': 'MasterGC_ContentBlockHolder_gvRepresentantesLegales_ctl02_proveedor'}) is None:
                pass
            else:
                tag = soup.find('a', attrs={'id': 'MasterGC_ContentBlockHolder_gvRepresentantesLegales_ctl02_proveedor'})
                proveedor_actual['representante_legal'] = tag.next_sibling.string.encode('utf-8')
                #rep_legal = rep_legal.strip().replace(',,', ',', 1).replace(',', ' ')

        la_lista[proveedor_actual['nit']] = proveedor_actual
    return la_lista


def load_compradores():
    """
    metodo encargado de llenar el diccionario
    de compradores para que sea facil y rapido usar su info
    cuando se generan los csv's
    """
    la_lista = {}
    for comprador in os.listdir('compradores/html/'):
        comprador_actual = {'nit':'',
                            'tipo':'',
                            'nombre':'',
                            'origenFondos':'',
                            'departamento':'',
                            'municipio':''}
        contenido = ''
        with open('compradores/html/{}'.format(comprador), 'r') as mydf:
            contenido = mydf.read()
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

        la_lista[comprador_actual['nombre']] = comprador_actual
    return la_lista


def gen_csv_comp():
    compradores = []
    campos = ['nit','tipo','nombre','origenFondos','departamento','municipio']
    compradores.append(campos)
    for comprador in os.listdir('compradores/html/'):
        row = []
        contenido = ''
        with open('compradores/html/{}'.format(comprador), 'r') as mydf:
            contenido = mydf.read()
        soup = BeautifulSoup(contenido, 'lxml')
        # NIT
        row.append(soup.find('span', attrs={'id': 'MasterGC_ContentBlockHolder_Lbl_Nit'}).string.encode('utf-8'))
        # tipo
        row.append(soup.find('tr', attrs={'id': 'MasterGC_ContentBlockHolder_trNit'}).next_sibling.next_sibling.contents[2].string.encode('utf-8'))
        # nombre
        row.append(soup.find('span', attrs={'id': 'MasterGC_ContentBlockHolder_lblEntidad'}).string.encode('utf-8'))
        # origen de fondos
        if soup.find('span', attrs={'id': 'MasterGC_ContentBlockHolder_LblEntidadSiaf'}) is not None:
            row.append(soup.find('span', attrs={'id': 'MasterGC_ContentBlockHolder_LblEntidadSiaf'}).string.encode('utf-8'))
        else:
            row.append('')
        # departamento
        row.append(soup.find('span', attrs={'id': 'MasterGC_ContentBlockHolder_lblDepartamento'}).string.encode('utf-8'))
        #municipio
        row.append(soup.find('span', attrs={'id': 'MasterGC_ContentBlockHolder_lblMunicipio'}).string.encode('utf-8'))

        compradores.append(row)


    with open('compradores/object/compradores.csv', 'wb') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_ALL)
        for pr in compradores:
            filewriter.writerow(pr)

def gen_csv_prov():
    """
    genera el csv de los proveedores a partir de
    los html's almacenados localmente
    """
    provs = []
    campos = ['nit','tipo','nombre','fechaConstitucion','inscripcionRM','representanteLegal']
    provs.append(campos)
    for proveedor in os.listdir('proveedores/html/'):
        row = []
        #print proveedor
        #proveedor = '1256716.html'
        #proveedor = '1030082.html'
        #proveedor = '11.html'
        #proveedor = '530841.html'
        #proveedor = '57573.html'
        contenido = ''
        with open('proveedores/html/{}'.format(proveedor), 'r') as mydf:
            contenido = mydf.read()
        soup = BeautifulSoup(contenido, 'lxml')
        row.append(soup.find('span', attrs={'id': 'MasterGC_ContentBlockHolder_lblNIT'}).string.encode('utf-8'))

        base = soup.find('div', attrs={'id': 'MasterGC_ContentBlockHolder_pnl_DatosInscripcion2'}).find('tr')
        # tipo
        tipo = base.contents[1].string
        row.append(tipo.encode('utf-8'))
        # nombre
        row.append(soup.find('span', attrs={'id': 'MasterGC_ContentBlockHolder_lblNombreProv'}).string.encode('utf-8'))
        if 'INDIVIDUAL' in tipo:
            # no hay
            # fecha de constitucion, repLegal, inscripcionRM
            row.append('')
            row.append('')
            row.append('')
        else:
            base = soup.find('div', attrs={'id': 'MasterGC_ContentBlockHolder_pnl_DatosInscripcion2'}).find('tr')
            #print len(base.parent.find_all('tr'))
            # fecha de constitucion
            # entra a este caso no no hay fecha de constitucion (ver 11.html)
            if len(base.parent.find_all('tr')) < 3:
                row.append('')
            else:
                row.append(base.next_sibling.next_sibling.contents[1].string.encode('utf-8'))
            # fecha de inscripcion Registro Mercantil
            #cuando se cumple esta condicion, la empresa solo es provisional (ver 1030082.html)
            if len(base.parent.find_all('tr')) < 5:
                row.append(base.next_sibling.contents[1].string.encode('utf-8'))
                #print '--'
            else:
                row.append(base.next_sibling.next_sibling.next_sibling.next_sibling.contents[1].string.encode('utf-8'))
            # representante legal, se quita la ',,' entre nombres y apellidos
            if soup.find('a', attrs={'id': 'MasterGC_ContentBlockHolder_gvRepresentantesLegales_ctl02_proveedor'}) is None:
                pass
            else:
                rep_legal = soup.find('a', attrs={'id': 'MasterGC_ContentBlockHolder_gvRepresentantesLegales_ctl02_proveedor'}).next_sibling.string
                rep_legal = rep_legal.strip()#.replace(',,', ',', 1).replace(',', ' ')
                row.append(rep_legal.encode('utf-8'))

        provs.append(row)

    with open('proveedores/object/proveedores.csv', 'wb') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_ALL)
        for pr in provs:
            filewriter.writerow(pr)
    

def gen_csv(adjudicaciones, campos, file):
    with open('adjudicaciones/adjudicaciones.csv', 'r') as mydf: 
        contenido = mydf.read()
        try:
            with open(file, 'ab') as csvfile:
                fieldnames = campos
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quotechar='|', quoting=csv.QUOTE_ALL)
                for adjudicacion in adjudicaciones:
                    writer.writerow(adjudicacion)
        except Exception:
            mydf.write(contenido)
            raise ValueError('error al escribir el csv del dia actual')

