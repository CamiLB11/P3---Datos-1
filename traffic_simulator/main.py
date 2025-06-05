from core.grafo import Grafo
from core.algoritmos import Dijkstra

grafo = Grafo()
grafo.agregar_nodo("A")
grafo.agregar_nodo("B")
grafo.agregar_nodo("C")

grafo.agregar_arista("A", "B", 5)
grafo.agregar_arista("B", "C", 3)
grafo.agregar_arista("A", "C", 10)

algoritmo = Dijkstra(grafo)
ruta = algoritmo.ruta_mas_corta("A", "C")
print("Ruta más corta:", ruta)
