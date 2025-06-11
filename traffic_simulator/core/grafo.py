from core.nodo import Nodo
from core.arista import Arista

class Grafo:
    def __init__(self):
        self.nodos = []

    def agregar_nodo(self, nombre):
        if not self.obtener_nodo(nombre):
            nuevo = Nodo(nombre)
            self.nodos.append(nuevo)
            return nuevo
        return None

    def agregar_arista(self, origen_nombre, destino_nombre, peso, bidireccional=True):
        origen = self.obtener_nodo(origen_nombre)
        destino = self.obtener_nodo(destino_nombre)

        if origen and destino:
            ## --Verificar si ya hay una arista entre dos ciudades
            existe = any(arista.destino.nombre == destino.nombre for arista in origen.vecinos)
            if bidireccional:
                existe |= any(arista.destino.nombre == origen.nombre for arista in destino.vecinos)

            if existe:
                print(f"Ya existe arista entre {origen_nombre} y {destino_nombre}")
                return

            ## --Crear arista
            arista = Arista(origen, destino, peso)
            origen.vecinos.append(arista)
            if bidireccional:
                arista2 = Arista(destino, origen, peso)
                destino.vecinos.append(arista2)


    def obtener_nodo(self, nombre):
        for nodo in self.nodos:
            if nodo.nombre == nombre:
                return nodo
        return None

    def bloquear_arista(self, origen_nombre, destino_nombre):
        origen = self.obtener_nodo(origen_nombre)
        if origen:
            for arista in origen.vecinos:
                if arista.destino.nombre == destino_nombre:
                    arista.activa = False

    def actualizar_peso_arista(self, origen_nombre, destino_nombre, nuevo_peso, bidireccional=True):
        origen = self.obtener_nodo(origen_nombre)
        destino = self.obtener_nodo(destino_nombre)

        if origen and destino:
            for arista in origen.vecinos:
                if arista.destino.nombre == destino_nombre and arista.activa:
                    arista.peso = nuevo_peso

            if bidireccional:
                for arista in destino.vecinos:
                    if arista.destino.nombre == origen_nombre and arista.activa:
                        arista.peso = nuevo_peso

    @property
    def adyacencias(self):
        ady = {}
        for nodo in self.nodos:
            ady[nodo.nombre] = {}
            for arista in nodo.vecinos:
                if arista.activa:
                    ady[nodo.nombre][arista.destino.nombre] = arista.peso
        return ady
