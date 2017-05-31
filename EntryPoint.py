"""
main module for this project
"""
import GtScraper as walker
import time
import os
lal = [None for x in range(10)]
lal[0] = 1
print lal
print lal.index(None)
start = time.time()
walker.scrape_month(2016, '01')

print('It took {0:0.1f} seconds'.format(time.time() - start))
"""
provs = {'123':{'nombre':'pepe', 'dir':'4calles'}}
provs['123']['buenas'] = 1243
if '12' in provs:
    print 'jeje'
else:
    print 'jiji'
#print provs['123']

def nose():
    global provs
    provs['12'] = {'algo':12,'que':'saber'}
    print provs
    print 'jeje'

def alguien():
    global provs
    provs['newkey'] = {'we':'are','the':1}
def lmp():
    global provs
    provs={}
print '**'
print provs
nose()
lmp()
alguien()
nose()
print provs
print '--'
"""
#NOTA MENTAL HACER LA LISTA DE TAMANIO X Y CUANDO YA NO HAYA ESPACIO IR REEMPLAZANDO DESDE EL INICIO HASTA EL FINAL
