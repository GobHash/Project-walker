
class Proveedor:
    def __init__(self, identificador, nombre):
        """Nombre del proveedor en cuestion """
        self.nombre = nombre
        """
        Esta puesto como identificador porque el proveedor puede ser una persona juridica (NIT)
        o una persona individual (CUI)
        """
        self.identificador = identificador
        self.direccion = []
        elp = nombre
        elp = elp + str(identificador)
        self.miHash = hash(elp)

    def agregarDireccion(self, direccion):
        self.direccion.append(direccion)
xf = Proveedor(124,"asdfsa")

