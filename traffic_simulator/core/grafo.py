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

    def agregar_arista(self, origen_nombre, destino_nombre, peso):
        origen = self.obtener_nodo(origen_nombre)
        destino = self.obtener_nodo(destino_nombre)
        if origen and destino:
            arista = Arista(origen, destino, peso)
            origen.vecinos.append(arista)

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
