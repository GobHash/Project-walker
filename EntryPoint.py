"""
main module for this project
takes comand-line args as it follows:

"""
import argparse
import datetime
import math
import os
import random
import time

import requests.exceptions as ex

import GtScraper as walker


def main():
    """
    funcion principal
    """
    if not os.path.exists('compradores/object'):
        os.makedirs('compradores/html')
        os.makedirs('compradores/object')
        open('compradores/object/compradores.csv', 'w').close()
    else: # ya existe el dir pero aseguramos crear el archivo
        if not os.path.isfile('compradores/object/compradores.csv'):
            open('compradores/object/compradores.csv', 'w').close()

    if not os.path.exists('proveedores/object'):
        os.makedirs('proveedores/html')
        os.makedirs('proveedores/object')
        open('proveedores/object/proveedores.csv', 'w').close()
    else: # ya existe el dir pero aseguramos crear el archivo
        if not os.path.isfile('proveedores/object/proveedores.csv'):
            open('proveedores/object/proveedores.csv', 'w').close()

    if not os.path.exists('adjudicaciones'):
        os.makedirs('adjudicaciones')
        open('adjudicaciones/adjudicaciones.csv', 'w').close()
    else: # ya existe el dir pero aseguramos crear el archivo
        if not os.path.isfile('adjudicaciones/adjudicaciones.csv'):
            open('adjudicaciones/adjudicaciones.csv', 'w').close()

    parser = argparse.ArgumentParser(description='Script to obtain information from guatecompras.gt and generate csv\'s with it')
    parser.add_argument('-y', '--year', help='year you wish to obtain data from, if no year is specified then today\'s info is obtained',
                        type=int)
    parser.add_argument('-m', '--month', help='month you wish to obtain data from',
                        type=int)
    parser.add_argument('-d', '--day', help='day you wish to obtain data from',
                        type=int)
    parser.add_argument('-v', "--verbose", type=int, choices=[1, 3],
                        default=3, help="increase output verbosity to log file (activity.log)")
    args = parser.parse_args()
    if args.verbose == 3:
        verbose = True
    else:
        verbose = False

    inicial = 60
    if args.year is None: # no viene el anio entonces voy a pedir solo el dia de hoy
        fecha = datetime.date.today()
        m_year = fecha.year
        m_month = fecha.month
        m_day = fecha.day
    elif args.month is None: # no viene el mes -> pido todo el anio
        m_year = args.year
        m_month = 15
        m_day = 33
    elif args.day is None: # no viene el dia -> pido todo el mes
        m_year = args.year
        m_month = args.month
        m_day = 33
    else:
        m_year = args.year
        m_month = args.month
        m_day = args.day

    continuar = True
    espera = inicial #segundos de espera inicial
    treshold = inicial*20
    max_ciclos = 5000
    ciclo_actual = 1
    walker.cargar_compradores()
    while continuar:
        try:
            walker.scrapedata(m_year, m_month, m_day)
            continuar = False

        except (ex.ConnectTimeout, ex.ChunkedEncodingError, ex.ConnectionError) as la_exception:
            print 'hay aumento en el tiempo de espera'
            if ciclo_actual >= max_ciclos:
                continuar = False
            else:
                if verbose:
                    print 'El siguiente error acaba de ocurrir: ', la_exception.message
                    print 'Se van a esperar {} segundos antes de volver a intentar conectar al servidor'.format(espera)
                time.sleep(espera)
                espera = math.ceil(espera*1.5)
                if espera > treshold:
                    espera = math.ceil(espera/random.randint(1, 6))
                    treshold = random.randint(math.floor(treshold*3/4), math.floor(treshold*7/5))
                    if verbose:
                        print 'El treshold de espera fue excedido, el nuevo es: {}'.format(treshold)
                if verbose:
                    print 'El nuevo tiempo de espera es de {} segundos'.format(espera)
                ciclo_actual += 1

if __name__ == "__main__":
    main()
