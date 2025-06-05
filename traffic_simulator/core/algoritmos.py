import math

class Dijkstra:
    def __init__(self, grafo):
        self.grafo = grafo

    def ruta_mas_corta(self, inicio_nombre, fin_nombre):
        distancias = {}
        previos = {}
        visitados = set()
        nodos = self.grafo.nodos

        for nodo in nodos:
            distancias[nodo.nombre] = math.inf
            previos[nodo.nombre] = None

        distancias[inicio_nombre] = 0

        while len(visitados) < len(nodos):
            nodo_actual = None
            menor_dist = math.inf

            #Busca el nodo no visitado con menor distancia
            for nodo in nodos:
                if nodo.nombre not in visitados and distancias[nodo.nombre] < menor_dist:
                    menor_dist = distancias[nodo.nombre]
                    nodo_actual = nodo

            if nodo_actual is None:
                break

            visitados.add(nodo_actual.nombre)

            for arista in nodo_actual.vecinos:
                if not arista.activa:
                    continue  #Salta las aristas bloqueadas
                vecino = arista.destino
                nueva_dist = distancias[nodo_actual.nombre] + arista.peso
                if nueva_dist < distancias[vecino.nombre]:
                    distancias[vecino.nombre] = nueva_dist
                    previos[vecino.nombre] = nodo_actual.nombre

        #Reconstruye la ruta
        camino = []
        actual = fin_nombre
        while actual is not None:
            camino.insert(0, actual)
            actual = previos[actual]

        return camino
