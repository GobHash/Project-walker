"""
este script es el encargado de generar las tuplas de tipo Adjudicacion
para que sean usadas por los otros modulos
"""
from collections import namedtuple
"""
detalles de pylint
los nombres de constantes deben ir todos en mayusculas
las variables van todas en minusculas
"""

Adjudicacion = namedtuple('Adjudicacion',
                          ["NOG", "Entidad", "Unidad_compradora", "Fecha_publicacion",
                           "Fecha_adjudicacion", "Costo_adjudicacion", "ID_proveedor",
                           "Nombre_proveedor"],
                          verbose=True, rename=True)
#esta linea es para que llene los defaults de la tupla que representa al proveedor
"""Adjudicacion.__new__.__defaults__ = (None,) * len(Adjudicacion._fields)

asd = Adjudicacion(NOG="98692")
L1 = [1,2]
asd.Fecha_adjudicacion = L1
"""

Prov = namedtuple("Prov", "ID, NM")

L1 = [1, 2]
ps = Prov(123, L1)
ps = ps._replace(ID=541)
print ps.ID