import pygame
import math
from random import randint
from core.algoritmos import Dijkstra


class Vehiculo:
    def __init__(self, ruta_posiciones, ruta_nombres, velocidad):
        self.ruta = ruta_posiciones
        self.ruta_nombres = ruta_nombres  # Nueva: nombres de ciudades en la ruta
        self.velocidad = velocidad
        self.indice = 0
        self.x, self.y = self.ruta[0] if self.ruta else (0, 0)
        self.radio = 10
        self.seleccionado = False  # Nueva: indica si está seleccionado
        self.color = (0, 0, 255)  # Azul por defecto
        self.color_seleccionado = (255, 0, 0)  # Rojo cuando está seleccionado
        self.id = randint(1000, 9999)  # ID único para identificar el vehículo

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
        # Cambiar color según si está seleccionado
        color = self.color_seleccionado if self.seleccionado else self.color
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.radio)

        # Dibujar ID del vehículo si está seleccionado
        if self.seleccionado:
            font = pygame.font.SysFont("Arial", 12)
            texto_id = font.render(f"ID:{self.id}", True, (255, 255, 255))
            screen.blit(texto_id, (int(self.x) - 20, int(self.y) - 25))

    def completado(self):
        return self.indice >= len(self.ruta) - 1

    def esta_en_posicion(self, mouse_pos, tolerancia=15):
        """Verifica si el mouse está cerca del vehículo"""
        distancia = math.hypot(mouse_pos[0] - self.x, mouse_pos[1] - self.y)
        return distancia <= tolerancia

    def seleccionar(self):
        """Selecciona el vehículo"""
        self.seleccionado = True

    def deseleccionar(self):
        """Deselecciona el vehículo"""
        self.seleccionado = False

    def obtener_info_ruta(self):
        """Retorna información de la ruta del vehículo"""
        origen = self.ruta_nombres[0] if self.ruta_nombres else "Desconocido"
        destino = self.ruta_nombres[-1] if self.ruta_nombres else "Desconocido"
        progreso = f"{self.indice + 1}/{len(self.ruta)}"
        return {
            "id": self.id,
            "origen": origen,
            "destino": destino,
            "ruta_completa": " -> ".join(self.ruta_nombres),
            "progreso": progreso,
            "completado": self.completado()
        }

    @staticmethod
    def crear_vehiculo(grafo, ciudades_colocadas, velocidad, carros):
        """Crear un nuevo vehículo con origen y destino aleatorios"""
        if len(ciudades_colocadas) >= 2:
            origen_nombre, _ = ciudades_colocadas[randint(0, len(ciudades_colocadas) - 1)]
            destino_nombre, _ = ciudades_colocadas[randint(0, len(ciudades_colocadas) - 1)]

            if origen_nombre != destino_nombre:
                algoritmo = Dijkstra(grafo)
                ruta_nombres = algoritmo.ruta_mas_corta(origen_nombre, destino_nombre)

                # Verificar que la ruta sea válida
                if len(ruta_nombres) > 1:  # Debe tener al menos origen y destino
                    ruta_posiciones = []
                    for nombre_ciudad in ruta_nombres:
                        pos = next((pos for nombre, pos in ciudades_colocadas if nombre == nombre_ciudad), None)
                        if pos:
                            ruta_posiciones.append(pos)

                    if len(ruta_posiciones) == len(ruta_nombres):  # Todas las posiciones encontradas
                        carro = Vehiculo(ruta_posiciones, ruta_nombres, velocidad)
                        carros.append(carro)
                        return carro
        return None


def dibujar_ruta_vehiculo(screen, vehiculo, ciudades_colocadas, font):
    """Dibuja la ruta completa de un vehículo seleccionado"""
    if not vehiculo.seleccionado or not vehiculo.ruta_nombres:
        return

    # Dibujar líneas de la ruta en color destacado
    for i in range(len(vehiculo.ruta) - 1):
        pygame.draw.line(screen, (255, 165, 0), vehiculo.ruta[i], vehiculo.ruta[i + 1], 4)  # Naranja grueso

    # Dibujar puntos de la ruta
    for i, (pos, nombre) in enumerate(zip(vehiculo.ruta, vehiculo.ruta_nombres)):
        if i == 0:  # Origen
            pygame.draw.circle(screen, (0, 255, 0), pos, 8)  # Verde
        elif i == len(vehiculo.ruta) - 1:  # Destino
            pygame.draw.circle(screen, (255, 0, 0), pos, 8)  # Rojo
        else:  # Puntos intermedios
            pygame.draw.circle(screen, (255, 165, 0), pos, 6)  # Naranja


def mostrar_info_vehiculo(screen, vehiculo, font):
    """Muestra información del vehículo seleccionado en pantalla"""
    if not vehiculo.seleccionado:
        return

    info = vehiculo.obtener_info_ruta()

    # Panel de información
    panel_x, panel_y = 10, 80
    panel_width, panel_height = 350, 120

    # Fondo del panel
    panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
    pygame.draw.rect(screen, (240, 240, 240), panel_rect)
    pygame.draw.rect(screen, (0, 0, 0), panel_rect, 2)

    # Información del vehículo
    textos = [
        f"VEHÍCULO SELECCIONADO",
        f"ID: {info['id']}",
        f"Origen: {info['origen']}",
        f"Destino: {info['destino']}",
        f"Progreso: {info['progreso']}",
        f"Ruta: {info['ruta_completa']}"
    ]

    for i, texto in enumerate(textos):
        color = (255, 0, 0) if i == 0 else (0, 0, 0)  # Título en rojo
        superficie_texto = font.render(texto, True, color)
        screen.blit(superficie_texto, (panel_x + 10, panel_y + 10 + i * 18))


def deseleccionar_todos_vehiculos(carros):
    """Deselecciona todos los vehículos"""
    for carro in carros:
        carro.deseleccionar()


def seleccionar_vehiculo_en_posicion(carros, mouse_pos):
    """Selecciona el vehículo más cercano a la posición del mouse"""
    vehiculo_mas_cercano = None
    distancia_minima = float('inf')

    for carro in carros:
        if carro.esta_en_posicion(mouse_pos):
            distancia = math.hypot(mouse_pos[0] - carro.x, mouse_pos[1] - carro.y)
            if distancia < distancia_minima:
                distancia_minima = distancia
                vehiculo_mas_cercano = carro

    if vehiculo_mas_cercano:
        deseleccionar_todos_vehiculos(carros)
        vehiculo_mas_cercano.seleccionar()
        return vehiculo_mas_cercano

    return None