import pygame
from core.grafo import Grafo
from core.algoritmos import Dijkstra
from utils import ciudades
from random import randint
from core.vehiculos import Vehiculo
from core.slider import Slider

pygame.init()
screen = pygame.display.set_mode((900, 600))
screen_title = pygame.display.set_caption("Traffic Simulator")
font = pygame.font.SysFont("Consolas", 18)
clock = pygame.time.Clock()
ciudad_seleccionada = None
ciudades_colocadas = []
grafo = Grafo()
carros = []
aristas = []
arista_seleccionada = None

slider = Slider((screen.get_width()/2,50), (200,10), 0.5, 0, 50)


## --Diccionario para las posiciones de la interfaz
ciudades_posiciones = {
    "Cartago": (23, 514),
    "San Jose": (152, 514),
    "Alajuela": (280, 514),
    "Heredia": (409, 514),
    "Limon": (538, 514),
    "Guanacaste": (666, 514),
    "Puntarenas": (795, 514)
}
## --Diccionario para los botones de las ciudades
ciudad_buttons = {
    f"{nombre}": ciudades.Ciudad("utils/ciudad.png", posicion)
    for nombre, posicion in ciudades_posiciones.items()
}

def main():
    global ciudad_seleccionada, arista_seleccionada
    punto1 = None
    punto2 = None
    velocidad = 0
    tiempo_carro = pygame.time.get_ticks()
    intervalo_carro = 500

    while True:
        screen.fill("white")
        mouse_pos = pygame.mouse.get_pos()
        mouse = pygame.mouse.get_pressed()

        ## --Dibujar slider
        if mouse[0]:
            if slider.container_rect.collidepoint(mouse_pos):
                slider.move_slider(pygame.mouse.get_pos())
        velocidad = slider.get_value()
        actualizar_velocidad(carros, velocidad)
        slider.render(screen)
        velocidad_text = font.render(f"Velocidad: {int(velocidad)}", False, (0,0,0))
        
        screen.blit(velocidad_text,velocidad_text.get_rect(midtop=(screen.get_width()/2, 20)))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return 

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                ## --Verificar si se selecciono alguna ciudad
                for nombre, boton in ciudad_buttons.items():
                    if boton.is_pressed():
                        ciudad_seleccionada = nombre
                        break
                else:
                    for nombre, posicion in ciudades_colocadas:
                        imagen = pygame.image.load("utils/ciudad.png").convert_alpha()
                        rect = imagen.get_rect(center=posicion)
                        if rect.collidepoint(mouse_pos):
                            if punto1 is None:
                                punto1 = nombre
                            elif punto2 is None:
                                punto2 = nombre
                                if punto1 != punto2:
                                    valor_arista = randint(0, 15)
                                    grafo.agregar_arista(punto1, punto2, valor_arista)
                                    aristas.append({
                                        "origen": punto1,
                                        "destino": punto2,
                                        "peso": valor_arista,
                                        "multiplicador": 1.0,
                                        "bloqueado" : False,
                                        "peso_original" : valor_arista
                                    })
                                else:
                                    print("Error")
                                punto1 = None
                                punto2 = None
                                break

                    ## --Si hay ciudad seleccionada y se coloca, la agrega a la lista
                    if ciudad_seleccionada and not any(nombre == ciudad_seleccionada for nombre, _ in ciudades_colocadas):
                        ciudades_colocadas.append((ciudad_seleccionada, mouse_pos))
                        print(f"{ciudad_seleccionada} colocada en {mouse_pos}")
                        grafo.agregar_nodo(ciudad_seleccionada)
                    else:
                        ciudad_seleccionada = None

                    ## --Verificar si se selecciona una arista
                    for ciudad_origen in grafo.adyacencias:
                        for ciudad_destino in grafo.adyacencias[ciudad_origen]:
                            pos_origen = next((pos for nombre, pos in ciudades_colocadas if nombre == ciudad_origen), None)
                            pos_destino = next((pos for nombre, pos in ciudades_colocadas if nombre == ciudad_destino), None)

                            if pos_origen and pos_destino:
                                if seleccionar_linea(mouse_pos[0], mouse_pos[1], *pos_origen, *pos_destino):
                                    arista_seleccionada = (ciudad_origen, ciudad_destino)
                
            ## --Aumentar o reducir peso 
            if event.type == pygame.KEYDOWN:
                if arista_seleccionada:
                    origen, destino = arista_seleccionada
                    nodo_origen = grafo.obtener_nodo(origen)
                    
                    peso_actual = None
                    for arista in nodo_origen.vecinos:
                        if arista.destino.nombre == destino and arista.activa:
                            peso_actual = arista.peso
                            break

                    if peso_actual is not None:
                        if event.key == pygame.K_UP:
                            nuevo_peso = peso_actual + 1
                            print(f"Nuevo peso de {origen} <-> {destino}: {nuevo_peso}")
                        elif event.key == pygame.K_DOWN:
                            nuevo_peso = max(0, peso_actual - 1)
                            print(f"Nuevo peso de {origen} <-> {destino}: {nuevo_peso}")
                        elif event.key == pygame.K_b:
                            for arista in aristas:
                                if (arista["origen"] == origen and arista["destino"] == destino) or \
                                (arista["origen"] == destino and arista["destino"] == origen):

                                    ## --Verificar si la arista esta bloqueada
                                    if not arista.get("bloqueado", False):
                                        ## --Bloquear la arista
                                        arista["peso_original"] = arista["peso"]
                                        nuevo_peso = 1000
                                        arista["bloqueado"] = True
                                        print(f"Arista entre {origen} y {destino} bloqueada")
                                    else:
                                        ## --Desbloquear la arista
                                        nuevo_peso = arista["peso_original"]
                                        arista["bloqueado"] = False
                                        print(f"Arista entre {origen} y {destino} desbloqueada")

                                    ## --Actualizar en el grafo
                                    grafo.actualizar_peso_arista(origen, destino, nuevo_peso)
                                    arista["peso"] = nuevo_peso
                        else:
                            nuevo_peso = peso_actual
                        grafo.actualizar_peso_arista(origen, destino, nuevo_peso)

                        ## --Actualiza el peso en la interfaz
                        for arista in aristas:
                            if (arista["origen"] == origen and arista["destino"] == destino) or \
                            (arista["origen"] == destino and arista["destino"] == origen):
                                arista["peso"] = nuevo_peso
                    
                ## --Generar vehiculos con 'C'    
                if event.key == pygame.K_c:
                    Vehiculo.crear_vehiculo(grafo, ciudades_colocadas, velocidad, carros)

            ## --Generar vehiculos cada 1 segundo
            tiempo_actual = pygame.time.get_ticks()
            if tiempo_actual - tiempo_carro >= intervalo_carro:
                Vehiculo.crear_vehiculo(grafo, ciudades_colocadas, velocidad, carros)
                tiempo_carro = tiempo_actual
                        

        ## --Dibujar aristas
        for ciudad_origen in grafo.adyacencias:
            for ciudad_destino, peso in grafo.adyacencias[ciudad_origen].items():
                pos_origen = next((pos for nombre, pos in ciudades_colocadas if nombre == ciudad_origen), None)
                pos_destino = next((pos for nombre, pos in ciudades_colocadas if nombre == ciudad_destino), None)

                if pos_origen and pos_destino:
                    color = color_aristas(peso)
                    pygame.draw.line(screen, color, pos_origen, pos_destino, 2)
                    ## --Dibujar el peso
                    mid_x = (pos_origen[0] + pos_destino[0]) // 2
                    mid_y = (pos_origen[1] + pos_destino[1]) // 2
                    peso_texto = font.render(str(peso), True, (0, 0, 0))
                    screen.blit(peso_texto, (mid_x, mid_y))

            
        ## --Dibujar carros
        for carro in carros[:]:
            carro.mover()
            carro.dibujar(screen)
            if carro.completado():
                carros.remove(carro)


        ## --Dibujar ciudades colocadas
        for nombre, posicion in ciudades_colocadas:
            imagen = pygame.image.load("utils/ciudad.png").convert_alpha()
            rect = imagen.get_rect(center=posicion)
            screen.blit(imagen, rect)

            texto = font.render(nombre, True, (0,0,0))
            texto_rect = texto.get_rect(midtop=(rect.centerx, rect.bottom + 5))
            screen.blit(texto, texto_rect)


        ## --Nombres para las ciudades
        ciudades_texto = {
            "Cartago": (30, 570),
            "San Jose": (152, 570),
            "Alajuela": (281, 570),
            "Heredia": (415, 570),
            "Limon": (554, 570),
            "Guanacaste": (659, 570),
            "Puntarenas": (786, 570)
        }
        for nombre, posicion in ciudades_texto.items():
            texto = font.render(nombre, False, (0,0,0))
            screen.blit(texto, posicion)       

        ## --Lineas que dividen los botones de ciudades
        lineas = [
            [(128,500), (128,600)],
            [(256,500), (256,600)],
            [(385,500), (385,600)],
            [(514,500), (514,600)],
            [(642,500), (642,600)],
            [(771,500), (771,600)],
            [(0,500), (900,500)],
        ]
        for x,y in lineas:
            pygame.draw.line(screen, "black", x,y)
        
        ## --Dibuja los botones en la pantalla
        for ciudad in ciudad_buttons.values():
            ciudad.draw(screen)

        
        pygame.display.flip()
        clock.tick(60)

## --Verificar si se hace click cerca de una linea 
def seleccionar_linea(px, py, x1, y1, x2, y2, dist_max=5):
    import math
    distancia = math.hypot(x2 - x1, y2 - y1) ## -Calcula la distancia entre los extremos de la linea
    if distancia == 0:
        return False
    
    ## -Verifica si se hizo click dentro o fuera de la linea
    u = ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / (distancia ** 2)
    if u < 0 or u > 1:
        return False
    ix = x1 + u * (x2 - x1)
    iy = y1 + u * (y2 - y1)
    return math.hypot(px - ix, py - iy) <= dist_max

## --Definir color dependiendo del peso
def color_aristas(peso, peso_min=1, peso_max=20):
    peso = max(peso_min, min(peso, peso_max))

    ## --Convierte el peso a un numero de 0 a 1
    porcentaje = (peso - peso_min) / (peso_max - peso_min)

    ## --Dependiendo del porcentaje, se pinta mas de un color u otro
    rojo = int(255 * porcentaje)
    verde = int(255 * (1 - porcentaje))
    return (rojo, verde, 0)

## --Actualiza la velocidad de los carros cuando se usa el slider
def actualizar_velocidad(carros, nueva_velocidad):
    for carro in carros:
        carro.velocidad = nueva_velocidad

if __name__ == '__main__':
    main()






