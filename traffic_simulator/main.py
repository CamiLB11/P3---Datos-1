import pygame
from core.grafo import Grafo
from core.algoritmos import Dijkstra
from utils import ciudades
from random import randint
from core.vehiculos import Vehiculo, dibujar_ruta_vehiculo, mostrar_info_vehiculo, deseleccionar_todos_vehiculos, \
    seleccionar_vehiculo_en_posicion
from core.slider import Slider
from core.analizador_trafico import AnalizadorTrafico

pygame.init()
screen = pygame.display.set_mode((900, 600))
screen_title = pygame.display.set_caption("Traffic Simulator")
font = pygame.font.SysFont("Consolas", 18)
font_small = pygame.font.SysFont("Consolas", 14)
clock = pygame.time.Clock()
ciudad_seleccionada = None
ciudades_colocadas = []
grafo = Grafo()
carros = []
aristas = []
arista_seleccionada = None
vehiculo_seleccionado = None
analizador = AnalizadorTrafico(grafo)
mostrar_recomendaciones = False
mostrar_mapa_calor = False
recomendaciones_actuales = None
ciudad_origen_alt = None
ciudad_destino_alt = None
rutas_alternativas_visibles = []

slider = Slider((screen.get_width() / 2, 50), (200, 10), 0.5, 0, 50)

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
    global mostrar_mapa_calor, rutas_alternativas_visibles, ciudad_origen_alt, ciudad_destino_alt, ciudad_seleccionada, arista_seleccionada, vehiculo_seleccionado, mostrar_recomendaciones, recomendaciones_actuales
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
        velocidad_text = font.render(f"Velocidad: {int(velocidad)}", False, (0, 0, 0))

        screen.blit(velocidad_text, velocidad_text.get_rect(midtop=(screen.get_width() / 2, 20)))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                click_procesado = False

                if event.button == 1:  # Clic izquierdo
                    vehiculo_clickeado = seleccionar_vehiculo_en_posicion(carros, mouse_pos)
                    if vehiculo_clickeado:
                        vehiculo_seleccionado = vehiculo_clickeado
                        print(f"Vehículo {vehiculo_clickeado.id} seleccionado")
                        click_procesado = True
                    else:
                        # Si no se seleccionó vehículo, deseleccionar todos
                        deseleccionar_todos_vehiculos(carros)
                        vehiculo_seleccionado = None

                ## --Solo procesar otros clicks si no se seleccionó un vehículo
                if not click_procesado:
                    ## --Verificar si se selecciono alguna ciudad
                    for nombre, boton in ciudad_buttons.items():
                        if boton.is_pressed():
                            ciudad_seleccionada = nombre
                            click_procesado = True
                            break

                    if not click_procesado:
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
                                            "bloqueado": False,
                                            "peso_original": valor_arista
                                        })
                                    else:
                                        print("Error: No puedes conectar una ciudad consigo misma")
                                    punto1 = None
                                    punto2 = None
                                    click_procesado = True
                                    break

                    ## --Si hay ciudad seleccionada y se coloca, la agrega a la lista
                    if not click_procesado and ciudad_seleccionada and not any(
                            nombre == ciudad_seleccionada for nombre, _ in ciudades_colocadas):
                        ciudades_colocadas.append((ciudad_seleccionada, mouse_pos))
                        print(f"{ciudad_seleccionada} colocada en {mouse_pos}")
                        grafo.agregar_nodo(ciudad_seleccionada)
                        ciudad_seleccionada = None
                        click_procesado = True

                    ## --Verificar si se selecciona una arista
                    if not click_procesado:
                        for ciudad_origen in grafo.adyacencias:
                            for ciudad_destino in grafo.adyacencias[ciudad_origen]:
                                pos_origen = next(
                                    (pos for nombre, pos in ciudades_colocadas if nombre == ciudad_origen), None)
                                pos_destino = next(
                                    (pos for nombre, pos in ciudades_colocadas if nombre == ciudad_destino), None)

                                if pos_origen and pos_destino:
                                    if seleccionar_linea(mouse_pos[0], mouse_pos[1], *pos_origen, *pos_destino):
                                        arista_seleccionada = (ciudad_origen, ciudad_destino)
                                        click_procesado = True
                                        break
                            if click_procesado:
                                break

            ## --Aumentar o reducir peso y bloquear aristas
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_1:
                    for nombre, posicion in ciudades_colocadas:
                        imagen = pygame.image.load("utils/ciudad.png").convert_alpha()
                        rect = imagen.get_rect(center=posicion)
                        if rect.collidepoint(mouse_pos):
                            ciudad_origen_alt = nombre
                            print(f"Ciudad origen para rutas alternativas: {ciudad_origen_alt}")

                if event.key == pygame.K_2:
                    for nombre, posicion in ciudades_colocadas:
                        imagen = pygame.image.load("utils/ciudad.png").convert_alpha()
                        rect = imagen.get_rect(center=posicion)
                        if rect.collidepoint(mouse_pos):
                            ciudad_destino_alt = nombre
                            print(f"Ciudad destino para rutas alternativas: {ciudad_destino_alt}")

                ## --Generar recomendaciones con 'R'
                if event.key == pygame.K_r:
                    print("Generando recomendaciones de tráfico...")
                    recomendaciones_actuales = analizador.generar_recomendaciones()
                    mostrar_recomendaciones = True

                ## --Ocultar recomendaciones con 'H'
                if event.key == pygame.K_h:
                    mostrar_recomendaciones = False

                ## -- Mostrar estadísticas con 'S'
                if event.key == pygame.K_s:
                    stats = analizador.obtener_estadisticas()
                    print("=== ESTADÍSTICAS DE TRÁFICO ===")
                    print(f"Vehículos procesados: {stats['total_vehiculos_procesados']}")
                    print(f"Aristas activas: {stats['total_aristas_activas']}")
                    print(f"Promedio vehículos/arista: {stats['promedio_vehiculos_por_arista']:.2f}")
                    if stats['arista_mas_usada']:
                        arista, flujo = stats['arista_mas_usada']
                        print(f"Arista más usada: {arista[0]} - {arista[1]} ({flujo} vehículos)")

                if event.key == pygame.K_t:
                    print("Iniciando análisis temporal...")
                    # Implementar análisis de patrones temporales

                # Tecla 'A' para mostrar rutas alternativas
                if event.key == pygame.K_a:
                    if ciudad_origen_alt and ciudad_destino_alt and ciudad_origen_alt != ciudad_destino_alt:
                        rutas_alt = analizador.detectar_rutas_alternativas(ciudad_origen_alt, ciudad_destino_alt)
                        rutas_alternativas_visibles = rutas_alt
                        print(
                            f"Encontradas {len(rutas_alt)} rutas alternativas entre {ciudad_origen_alt} y {ciudad_destino_alt}")
                    else:
                        print(
                            "Debes seleccionar origen (tecla 1) y destino (tecla 2) distintos antes de mostrar rutas alternativas")

                # Tecla 'M' para mapa de calor
                if event.key == pygame.K_m:
                    mostrar_mapa_calor = not mostrar_mapa_calor  # Variable global a agregar

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

                        if event.key in [pygame.K_UP, pygame.K_DOWN]:
                            grafo.actualizar_peso_arista(origen, destino, nuevo_peso)
                            ## --Actualiza el peso en la interfaz
                            for arista in aristas:
                                if (arista["origen"] == origen and arista["destino"] == destino) or \
                                        (arista["origen"] == destino and arista["destino"] == origen):
                                    arista["peso"] = nuevo_peso

                ## --Generar vehiculos con 'C'
                if event.key == pygame.K_c:
                    nuevo_vehiculo = Vehiculo.crear_vehiculo(grafo, ciudades_colocadas, velocidad, carros)
                    if nuevo_vehiculo:
                        print(f"Vehículo {nuevo_vehiculo.id} creado")

                ## --Deseleccionar vehículo con ESC
                if event.key == pygame.K_ESCAPE:
                    deseleccionar_todos_vehiculos(carros)
                    vehiculo_seleccionado = None
                    print("Vehículo deseleccionado")

        ## --Generar vehiculos automáticamente cada intervalo
        tiempo_actual = pygame.time.get_ticks()
        if tiempo_actual - tiempo_carro >= intervalo_carro:
            Vehiculo.crear_vehiculo(grafo, ciudades_colocadas, velocidad, carros)
            tiempo_carro = tiempo_actual

        if mostrar_mapa_calor:
            indices_congestion = analizador.calcular_indice_congestion()
            dibujar_mapa_calor_congestion(screen, grafo, indices_congestion, ciudades_colocadas)

        ## --Dibujar aristas (ANTES que las rutas de vehículos)
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

        # Dibujar rutas alternativas si están disponibles
        if rutas_alternativas_visibles:
            dibujar_rutas_alternativas(screen, rutas_alternativas_visibles, ciudades_colocadas)

        ## -- Dibujar ruta del vehículo seleccionado (DESPUÉS de las aristas normales)
        if vehiculo_seleccionado:
            dibujar_ruta_vehiculo(screen, vehiculo_seleccionado, ciudades_colocadas, font)

        ## --Dibujar carros
        for carro in carros[:]:
            carro.mover()
            carro.dibujar(screen)
            if carro.completado():
                analizador.registrar_vehiculo(carro.ruta_nombres)
                if carro == vehiculo_seleccionado:
                    vehiculo_seleccionado = None
                carros.remove(carro)

        ## --Dibujar ciudades colocadas
        for nombre, posicion in ciudades_colocadas:
            imagen = pygame.image.load("utils/ciudad.png").convert_alpha()
            rect = imagen.get_rect(center=posicion)
            screen.blit(imagen, rect)

            texto = font.render(nombre, True, (0, 0, 0))
            texto_rect = texto.get_rect(midtop=(rect.centerx, rect.bottom + 5))
            screen.blit(texto, texto_rect)

        # Mostrar puntos críticos si hay recomendaciones activas
        if mostrar_recomendaciones and recomendaciones_actuales:
            puntos_criticos = recomendaciones_actuales.get('puntos_criticos', [])
            for punto in puntos_criticos:
                nombre = punto['nodo']
                pos = next((p for n, p in ciudades_colocadas if n == nombre), None)
                if pos:
                    pygame.draw.circle(screen, (255, 0, 0), pos, 10, 2)  # círculo rojo

        if mostrar_recomendaciones and recomendaciones_actuales:
            dibujar_recomendaciones(screen, recomendaciones_actuales, font_small)

        ## -- Mostrar información del vehículo seleccionado
        if vehiculo_seleccionado:
            mostrar_info_vehiculo(screen, vehiculo_seleccionado, font_small)

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
            texto = font.render(nombre, False, (0, 0, 0))
            screen.blit(texto, posicion)

            ## --Lineas que dividen los botones de ciudades
        lineas = [
            [(128, 500), (128, 600)],
            [(256, 500), (256, 600)],
            [(385, 500), (385, 600)],
            [(514, 500), (514, 600)],
            [(642, 500), (642, 600)],
            [(771, 500), (771, 600)],
            [(0, 500), (900, 500)],
        ]
        for x, y in lineas:
            pygame.draw.line(screen, "black", x, y)

        ## --Dibuja los botones en la pantalla
        for ciudad in ciudad_buttons.values():
            ciudad.draw(screen)

        ## -- Mostrar instrucciones
        instrucciones = [
            "Click en vehículo para seleccionar",
            "ESC para deseleccionar",
            "C para crear vehículo manual",
            "R para generar recomendaciones",
            "H para ocultar recomendaciones",
            "S para mostrar estadísticas"
        ]

        for i, instruccion in enumerate(instrucciones):
            texto_instr = font_small.render(instruccion, True, (100, 100, 100))
            screen.blit(texto_instr, (10, 200 + i * 15))

        pygame.display.flip()
        clock.tick(60)


def dibujar_recomendaciones(screen, recomendaciones, font):
    """Versión mejorada del panel de recomendaciones"""
    panel_x, panel_y = 450, 80
    panel_width, panel_height = 430, 450

    # Fondo con transparencia
    panel_surface = pygame.Surface((panel_width, panel_height))
    panel_surface.set_alpha(240)
    panel_surface.fill((250, 250, 250))
    screen.blit(panel_surface, (panel_x, panel_y))

    # Borde
    pygame.draw.rect(screen, (50, 50, 50), (panel_x, panel_y, panel_width, panel_height), 3)

    y_offset = 10

    # Título con eficiencia de red
    eficiencia = recomendaciones.get('eficiencia_red', 0)
    titulo = f"ANÁLISIS DE TRÁFICO - Eficiencia: {eficiencia:.2f}"
    color_titulo = (0, 150, 0) if eficiencia > 0.7 else (200, 100, 0) if eficiencia > 0.4 else (200, 0, 0)
    superficie_titulo = font.render(titulo, True, color_titulo)
    screen.blit(superficie_titulo, (panel_x + 10, panel_y + y_offset))
    y_offset += 25

    # Separador
    pygame.draw.line(screen, (100, 100, 100),
                     (panel_x + 10, panel_y + y_offset),
                     (panel_x + panel_width - 10, panel_y + y_offset), 2)
    y_offset += 15

    prioridades = recomendaciones.get('prioridades', [])
    if prioridades:
        subtitulo = font.render("PRIORIDADES:", True, (150, 0, 0))
        screen.blit(subtitulo, (panel_x + 10, panel_y + y_offset))
        y_offset += 18

        for i, prioridad in enumerate(prioridades[:3]):  # Top 3 prioridades
            color_prioridad = (200, 0, 0) if prioridad['prioridad'] == 1 else (200, 100, 0) if prioridad[
                                                                                                   'prioridad'] == 2 else (
                100, 100, 100)
            texto = f"P{prioridad['prioridad']}: {prioridad['tipo']}"
            superficie = font.render(texto, True, color_prioridad)
            screen.blit(superficie, (panel_x + 20, panel_y + y_offset))
            y_offset += 15

            # Descripción en línea siguiente
            desc_texto = f"   {prioridad['descripcion'][:45]}..."
            superficie_desc = font.render(desc_texto, True, (60, 60, 60))
            screen.blit(superficie_desc, (panel_x + 25, panel_y + y_offset))
            y_offset += 15
        y_offset += 10

    congestion = recomendaciones.get('congestion', {})
    if congestion:
        subtitulo = font.render("ESTADO DE CONGESTIÓN:", True, (150, 0, 0))
        screen.blit(subtitulo, (panel_x + 10, panel_y + y_offset))
        y_offset += 18

        # Mostrar solo las más congestionadas
        aristas_criticas = [(k, v) for k, v in congestion.items() if v['nivel'] in ['Alto', 'Crítico']]
        for arista_key, info in aristas_criticas[:3]:
            color_nivel = (200, 0, 0) if info['nivel'] == 'Crítico' else (200, 100, 0)
            texto = f"• {arista_key[0]}-{arista_key[1]}: {info['nivel']}"
            superficie = font.render(texto, True, color_nivel)
            screen.blit(superficie, (panel_x + 20, panel_y + y_offset))
            y_offset += 15
        y_offset += 10

    predicciones = recomendaciones.get('predicciones', {})
    if predicciones:
        subtitulo = font.render("PREDICCIONES:", True, (150, 0, 0))
        screen.blit(subtitulo, (panel_x + 10, panel_y + y_offset))
        y_offset += 18

        pred_crecientes = [(k, v) for k, v in predicciones.items() if v['tendencia'] == 'Creciente']
        for arista_key, pred in pred_crecientes[:2]:
            texto = f"• {arista_key[0]}-{arista_key[1]}: ↑ Creciente"
            superficie = font.render(texto, True, (200, 100, 0))
            screen.blit(superficie, (panel_x + 20, panel_y + y_offset))
            y_offset += 15
        y_offset += 10

    # Resto de recomendaciones existentes (versión condensada)
    if recomendaciones.get('puntos_criticos'):
        subtitulo = font.render("PUNTOS CRÍTICOS:", True, (150, 0, 0))
        screen.blit(subtitulo, (panel_x + 10, panel_y + y_offset))
        y_offset += 18

        for punto in recomendaciones['puntos_criticos'][:2]:
            texto = f"• {punto['nodo']} ({punto['centralidad']:.3f})"
            superficie = font.render(texto, True, (0, 0, 0))
            screen.blit(superficie, (panel_x + 20, panel_y + y_offset))
            y_offset += 15

    # Instrucciones
    y_offset = panel_height - 45
    instrucciones = [
        "R: Actualizar análisis | H: Ocultar | S: Estadísticas",
        "T: Análisis temporal | A: Rutas alternativas"
    ]

    for instruccion in instrucciones:
        superficie_instr = font.render(instruccion, True, (100, 100, 100))
        screen.blit(superficie_instr, (panel_x + 10, panel_y + y_offset))
        y_offset += 15


def dibujar_mapa_calor_congestion(screen, grafo, congestion, ciudades_colocadas):
    """Dibuja un mapa de calor de congestión en las aristas"""
    for arista_key, info in congestion.items():
        origen_nombre, destino_nombre = arista_key

        pos_origen = next((pos for nombre, pos in ciudades_colocadas if nombre == origen_nombre), None)
        pos_destino = next((pos for nombre, pos in ciudades_colocadas if nombre == destino_nombre), None)

        if pos_origen and pos_destino:
            # Color basado en nivel de congestión
            if info['nivel'] == 'Crítico':
                color = (255, 0, 0)  # Rojo
                grosor = 6
            elif info['nivel'] == 'Alto':
                color = (255, 100, 0)  # Naranja
                grosor = 4
            elif info['nivel'] == 'Medio':
                color = (255, 255, 0)  # Amarillo
                grosor = 3
            else:
                color = (0, 255, 0)  # Verde
                grosor = 2

            pygame.draw.line(screen, color, pos_origen, pos_destino, grosor)

            # Mostrar índice de congestión
            mid_x = (pos_origen[0] + pos_destino[0]) // 2
            mid_y = (pos_origen[1] + pos_destino[1]) // 2
            font_small = pygame.font.SysFont("Consolas", 12)
            indice_texto = f"{info['indice']:.2f}"
            superficie_indice = font_small.render(indice_texto, True, (255, 255, 255))

            # Fondo para el texto
            rect_fondo = superficie_indice.get_rect(center=(mid_x, mid_y))
            pygame.draw.rect(screen, (0, 0, 0), rect_fondo.inflate(4, 2))
            screen.blit(superficie_indice, rect_fondo)


def dibujar_rutas_alternativas(screen, rutas_alternativas, ciudades_colocadas):
    """Visualiza rutas alternativas encontradas"""
    colores = [(0, 255, 0), (0, 0, 255), (255, 0, 255)]  # Verde, Azul, Magenta

    for i, ruta_info in enumerate(rutas_alternativas):
        if i >= len(colores):
            break

        ruta = ruta_info['ruta']
        color = colores[i]
        grosor = 3 if ruta_info['tipo'] == 'Principal' else 2

        # Dibujar la ruta
        for j in range(len(ruta) - 1):
            pos_origen = next((pos for nombre, pos in ciudades_colocadas if nombre == ruta[j]), None)
            pos_destino = next((pos for nombre, pos in ciudades_colocadas if nombre == ruta[j + 1]), None)

            if pos_origen and pos_destino:
                pygame.draw.line(screen, color, pos_origen, pos_destino, grosor)

        # Etiqueta de la ruta
        if len(ruta) > 0:
            pos_inicio = next((pos for nombre, pos in ciudades_colocadas if nombre == ruta[0]), None)
            if pos_inicio:
                font_small = pygame.font.SysFont("Consolas", 12)
                etiqueta = f"{ruta_info['tipo']} ({ruta_info['peso']})"
                superficie_etiqueta = font_small.render(etiqueta, True, color)
                screen.blit(superficie_etiqueta, (pos_inicio[0] + 15, pos_inicio[1] - 15 - i * 15))


## --Funciones auxiliares (sin cambios)
def seleccionar_linea(px, py, x1, y1, x2, y2, dist_max=5):
    import math
    distancia = math.hypot(x2 - x1, y2 - y1)
    if distancia == 0:
        return False

    u = ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / (distancia ** 2)
    if u < 0 or u > 1:
        return False
    ix = x1 + u * (x2 - x1)
    iy = y1 + u * (y2 - y1)
    return math.hypot(px - ix, py - iy) <= dist_max


def color_aristas(peso, peso_min=1, peso_max=20):
    peso = max(peso_min, min(peso, peso_max))
    porcentaje = (peso - peso_min) / (peso_max - peso_min)
    rojo = int(255 * porcentaje)
    verde = int(255 * (1 - porcentaje))
    return (rojo, verde, 0)


def actualizar_velocidad(carros, nueva_velocidad):
    for carro in carros:
        carro.velocidad = nueva_velocidad


if __name__ == '__main__':
    main()