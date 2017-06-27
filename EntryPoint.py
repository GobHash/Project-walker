"""
main module for this project
takes comand-line args as it follows:

"""
import argparse
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

    if not os.path.exists('compradores/object'):
        os.makedirs('proveedores/html')
        os.makedirs('proveedores/object')
        open('proveedores/object/proveedores.csv', 'w').close()

    if not os.path.exists('adjudicaciones'):
        os.makedirs('adjudicaciones')
        open('adjudicaciones/adjudicaciones.csv', 'w').close()

    parser = argparse.ArgumentParser(description='Script to obtain information from guatecompras.gt and generate csv\'s with it')
    parser.add_argument('year', help='year you wish to obtain data from',
                        type=int)
    parser.add_argument('-m', '--month', help='month you wish to obtain data from',
                        type=int)
    parser.add_argument('-d', '--day', help='day you wish to obtain data from',
                        type=int)
    parser.add_argument('-w', '--wait', help='initial number of seconds to wait before reconnecting to host, will grow eventually',
                        type=int, default=60)
    parser.add_argument('-v', "--verbose", type=int, choices=[1, 3],
                        default=3, help="increase output verbosity to log file (activity.log)")
    args = parser.parse_args()
    if args.verbose == 3:
        verbose = True
    else:
        verbose = False

    inicial = args.wait
    m_year = args.year
    if args.month < 10:
        m_month = '0' + str(args.month)
    else:
        m_month = str(args.month)

    continuar = True
    espera = inicial #segundos de espera inicial
    treshold = inicial*20
    max_ciclos = 5000
    ciclo_actual = 1
    walker.cargar_compradores()
    while continuar:
        try:
            walker.scrape_month(m_year, m_month)
            continuar = False
            print 'el tiempo final de espera fue de {}'.format(espera)

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
