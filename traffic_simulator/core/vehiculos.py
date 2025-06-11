import pygame
import math
from random import randint
from core.algoritmos import Dijkstra

class Vehiculo:
    def __init__(self, ruta_posiciones, velocidad):
        self.ruta = ruta_posiciones
        self.velocidad = velocidad
        self.indice = 0
        self.x, self.y = self.ruta[0] if self.ruta else (0, 0)
        self.radio = 10

    def mover(self):
        if self.indice >= len(self.ruta) - 1:
            return 

        objetivo = self.ruta[self.indice + 1]
        dx = objetivo[0] - self.x
        dy = objetivo[1] - self.y
        distancia = math.hypot(dx, dy)

        if distancia < self.velocidad:
            self.x, self.y = objetivo
            self.indice += 1
        else:
            self.x += self.velocidad * dx / distancia
            self.y += self.velocidad * dy / distancia

    def dibujar(self, screen):
        pygame.draw.circle(screen, (0, 0, 255), (int(self.x), int(self.y)), self.radio)

    def completado(self):
        return self.indice >= len(self.ruta) -1
    
     ## --Elegir aleatoriamente origen y destino
    def crear_vehiculo(grafo, ciudades_colocadas, velocidad, carros):
        if len(ciudades_colocadas) >= 2:
            origen_nombre, _ = ciudades_colocadas[randint(0, len(ciudades_colocadas) - 1)]
            destino_nombre, _ = ciudades_colocadas[randint(0, len(ciudades_colocadas) - 1)]

            if origen_nombre != destino_nombre:
                algoritmo = Dijkstra(grafo)
                ruta_nombres = algoritmo.ruta_mas_corta(origen_nombre, destino_nombre)

                ruta_posiciones = [
                    next(pos for nombre, pos in ciudades_colocadas if nombre == nombre_ciudad)
                    for nombre_ciudad in ruta_nombres
                ]

                carro = Vehiculo(ruta_posiciones, velocidad)
                carros.append(carro)
