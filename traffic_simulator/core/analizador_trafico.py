# Mejoras sugeridas para analizador_trafico.py

import math
from collections import defaultdict
import heapq


class AnalizadorTrafico:
    def __init__(self, grafo):
        self.grafo = grafo
        self.flujo_vehicular = defaultdict(int)
        self.tiempos_promedio = defaultdict(list)
        self.historial_flujo = defaultdict(list)  # NUEVO: Historial temporal
        self.capacidades_aristas = defaultdict(lambda: 10)  # NUEVO: Capacidades por defecto

    def calcular_eficiencia_red(self):
        """ Calcula la eficiencia general de la red"""
        from core.algoritmos import Dijkstra

        dijkstra = Dijkstra(self.grafo)
        nodos = [nodo.nombre for nodo in self.grafo.nodos]
        n = len(nodos)

        if n < 2:
            return 0

        suma_eficiencias = 0
        pares_conectados = 0

        for i, origen in enumerate(nodos):
            for j, destino in enumerate(nodos):
                if i < j:  # Evitar duplicados
                    try:
                        ruta = dijkstra.ruta_mas_corta(origen, destino)
                        if len(ruta) > 1:
                            # Calcular distancia euclidiana vs distancia de ruta
                            pos_origen = self.obtener_posicion_nodo(origen)
                            pos_destino = self.obtener_posicion_nodo(destino)

                            if pos_origen and pos_destino:
                                dist_euclidiana = math.hypot(
                                    pos_destino[0] - pos_origen[0],
                                    pos_destino[1] - pos_origen[1]
                                )
                                dist_ruta = self.calcular_distancia_ruta(ruta)

                                if dist_ruta > 0:
                                    eficiencia = dist_euclidiana / dist_ruta
                                    suma_eficiencias += eficiencia
                                    pares_conectados += 1
                    except:
                        continue

        return suma_eficiencias / max(1, pares_conectados)

    def detectar_rutas_alternativas(self, origen, destino, k=3):
        """ Encuentra las k rutas más cortas alternativas"""
        from core.algoritmos import Dijkstra

        dijkstra = Dijkstra(self.grafo)
        rutas_alternativas = []

        try:
            # Ruta principal
            ruta_principal = dijkstra.ruta_mas_corta(origen, destino)
            if len(ruta_principal) > 1:
                rutas_alternativas.append({
                    'ruta': ruta_principal,
                    'peso': self.calcular_peso_ruta(ruta_principal),
                    'tipo': 'Principal'
                })

            # Buscar rutas alternativas bloqueando aristas de la ruta principal
            for i in range(len(ruta_principal) - 1):
                nodo_actual = ruta_principal[i]
                nodo_siguiente = ruta_principal[i + 1]

                # Temporalmente bloquear esta arista
                peso_original = self.bloquear_arista_temporal(nodo_actual, nodo_siguiente)

                try:
                    ruta_alt = dijkstra.ruta_mas_corta(origen, destino)
                    if len(ruta_alt) > 1 and ruta_alt != ruta_principal:
                        rutas_alternativas.append({
                            'ruta': ruta_alt,
                            'peso': self.calcular_peso_ruta(ruta_alt),
                            'tipo': 'Alternativa'
                        })
                except:
                    pass

                # Restaurar arista
                self.restaurar_arista_temporal(nodo_actual, nodo_siguiente, peso_original)

            # Ordenar por peso y retornar las k mejores
            rutas_alternativas.sort(key=lambda x: x['peso'])
            return rutas_alternativas[:k]

        except:
            return []

    def calcular_indice_congestion(self):
        """ Calcula un índice de congestión para cada arista"""
        indices_congestion = {}

        for arista_key, flujo in self.flujo_vehicular.items():
            capacidad = self.capacidades_aristas[arista_key]
            indice = flujo / capacidad if capacidad > 0 else 0

            # Clasificar nivel de congestión
            if indice < 0.3:
                nivel = "Bajo"
            elif indice < 0.7:
                nivel = "Medio"
            elif indice < 1.0:
                nivel = "Alto"
            else:
                nivel = "Crítico"

            indices_congestion[arista_key] = {
                'indice': indice,
                'nivel': nivel,
                'flujo': flujo,
                'capacidad': capacidad
            }

        return indices_congestion

    def predecir_congestion_futura(self):
        """ Predice congestión basada en tendencias históricas"""
        predicciones = {}

        for arista_key, historial in self.historial_flujo.items():
            if len(historial) >= 3:
                # Calcular tendencia (regresión lineal simple)
                n = len(historial)
                x_vals = list(range(n))
                y_vals = historial

                # Fórmulas de regresión lineal
                sum_x = sum(x_vals)
                sum_y = sum(y_vals)
                sum_xy = sum(x * y for x, y in zip(x_vals, y_vals))
                sum_x2 = sum(x * x for x in x_vals)

                pendiente = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
                intercepto = (sum_y - pendiente * sum_x) / n

                # Predicción para el siguiente período
                prediccion = pendiente * n + intercepto

                predicciones[arista_key] = {
                    'tendencia': 'Creciente' if pendiente > 0.1 else 'Decreciente' if pendiente < -0.1 else 'Estable',
                    'prediccion': max(0, int(prediccion)),
                    'confianza': min(1.0, len(historial) / 10)  # Más datos = más confianza
                }

        return predicciones

    def generar_recomendaciones_avanzadas(self):
        """ Genera recomendaciones más sofisticadas"""
        recomendaciones = {
            'puntos_criticos': [],
            'cuellos_botella': [],
            'puntos_articulacion': [],
            'rutas_alternativas': [],
            'eficiencia_red': 0,
            'congestion': {},
            'predicciones': {},
            'recomendaciones_generales': [],
            'prioridades': []
        }

        # Análisis existente
        centralidad = self.calcular_centralidad_intermediacion()
        cuellos_botella = self.identificar_cuellos_botella()
        puntos_articulacion = self.analizar_conectividad()

        # Nuevos análisis
        eficiencia = self.calcular_eficiencia_red()
        congestion = self.calcular_indice_congestion()
        predicciones = self.predecir_congestion_futura()

        # Llenar recomendaciones
        recomendaciones['puntos_criticos'] = self.formatear_puntos_criticos(centralidad)
        recomendaciones['cuellos_botella'] = cuellos_botella[:3]
        recomendaciones['puntos_articulacion'] = puntos_articulacion
        recomendaciones['eficiencia_red'] = eficiencia
        recomendaciones['congestion'] = congestion
        recomendaciones['predicciones'] = predicciones

        # Generar recomendaciones priorizadas
        recomendaciones['prioridades'] = self.generar_prioridades(
            centralidad, cuellos_botella, puntos_articulacion, congestion, predicciones
        )

        # Sugerir rutas alternativas para los puntos más críticos
        nodos_criticos = [p['nodo'] for p in recomendaciones['puntos_criticos']]
        if len(nodos_criticos) >= 2:
            rutas_alt = self.detectar_rutas_alternativas(nodos_criticos[0], nodos_criticos[1])
            recomendaciones['rutas_alternativas'] = rutas_alt

        return recomendaciones

    def generar_prioridades(self, centralidad, cuellos_botella, puntos_articulacion, congestion, predicciones):
        """Genera lista de prioridades de acción"""
        prioridades = []

        # Prioridad 1: Puntos críticos con congestión alta
        for arista_key, info_congestion in congestion.items():
            if info_congestion['nivel'] in ['Alto', 'Crítico']:
                prioridades.append({
                    'prioridad': 1,
                    'tipo': 'Congestión Crítica',
                    'descripcion': f"Arista {arista_key[0]}-{arista_key[1]} con congestión {info_congestion['nivel'].lower()}",
                    'accion': 'Aumentar capacidad o crear ruta alternativa',
                    'impacto': 'Alto'
                })

        # Prioridad 2: Puntos de articulación
        for punto in puntos_articulacion:
            prioridades.append({
                'prioridad': 2,
                'tipo': 'Punto de Articulación',
                'descripcion': f"Nodo {punto['nodo']} es crítico para conectividad",
                'accion': 'Crear conexiones redundantes',
                'impacto': 'Alto'
            })

        # Prioridad 3: Predicciones de congestión creciente
        for arista_key, pred in predicciones.items():
            if pred['tendencia'] == 'Creciente' and pred['confianza'] > 0.5:
                prioridades.append({
                    'prioridad': 3,
                    'tipo': 'Congestión Futura',
                    'descripcion': f"Arista {arista_key[0]}-{arista_key[1]} tendrá congestión creciente",
                    'accion': 'Planificar expansión preventiva',
                    'impacto': 'Medio'
                })

        return sorted(prioridades, key=lambda x: x['prioridad'])

    # Funciones auxiliares
    def obtener_posicion_nodo(self, nombre_nodo):
        """Obtiene la posición visual de un nodo (implementar según tu sistema)"""
        # Esta función debería conectarse con ciudades_colocadas del main
        return None

    def calcular_distancia_ruta(self, ruta):
        """Calcula la distancia total de una ruta"""
        distancia = 0
        for i in range(len(ruta) - 1):
            peso = self.obtener_peso_arista(ruta[i], ruta[i + 1])
            distancia += peso
        return distancia

    def calcular_betweenness_centrality_optimizado(self):
        """Versión optimizada del cálculo de centralidad"""
        from collections import defaultdict, deque

        centrality = defaultdict(float)
        nodes = [nodo.nombre for nodo in self.grafo.nodos]

        for s in nodes:
            # Algoritmo de Brandes para centralidad de intermediación
            stack = []
            paths = defaultdict(list)
            sigma = defaultdict(int)
            sigma[s] = 1
            d = defaultdict(lambda: -1)
            d[s] = 0
            queue = deque([s])

            # BFS
            while queue:
                v = queue.popleft()
                stack.append(v)

                nodo_v = self.grafo.obtener_nodo(v)
                if nodo_v:
                    for arista in nodo_v.vecinos:
                        w = arista.destino.nombre
                        if d[w] < 0:
                            queue.append(w)
                            d[w] = d[v] + 1
                        if d[w] == d[v] + 1:
                            sigma[w] += sigma[v]
                            paths[w].append(v)

            # Acumulación
            delta = defaultdict(float)
            while stack:
                w = stack.pop()
                for v in paths[w]:
                    delta[v] += (sigma[v] / sigma[w]) * (1 + delta[w])
                if w != s:
                    centrality[w] += delta[w]

        # Normalizar
        n = len(nodes)
        normalization = 2.0 / ((n - 1) * (n - 2)) if n > 2 else 1.0
        for node in centrality:
            centrality[node] *= normalization

        return dict(centrality)

    def analizar_vulnerabilidad_red(self):
        """Analiza la vulnerabilidad de la red a fallos"""
        vulnerabilidades = {
            'nodos_criticos': [],
            'aristas_criticas': [],
            'componentes_conexas': 0,
            'robustez': 0.0
        }

        # Análisis de nodos críticos (puntos de articulación)
        puntos_articulacion = self.encontrar_puntos_articulacion()
        for punto in puntos_articulacion:
            # Simular eliminación del nodo
            componentes_antes = self.contar_componentes_conexas()
            componentes_despues = self.contar_componentes_conexas_sin_nodo(punto)

            vulnerabilidades['nodos_criticos'].append({
                'nodo': punto,
                'impacto': componentes_despues - componentes_antes,
                'nivel': 'Crítico' if componentes_despues > componentes_antes + 1 else 'Alto'
            })

        # Análisis de aristas críticas (puentes)
        puentes = self.encontrar_puentes()
        for origen, destino in puentes:
            vulnerabilidades['aristas_criticas'].append({
                'arista': (origen, destino),
                'tipo': 'Puente',
                'impacto': 'Desconexión de componentes'
            })

        # Calcular robustez de la red
        total_nodos = len([nodo.nombre for nodo in self.grafo.nodos])
        nodos_criticos = len(vulnerabilidades['nodos_criticos'])
        vulnerabilidades['robustez'] = 1.0 - (nodos_criticos / max(1, total_nodos))

        return vulnerabilidades

    def generar_plan_mejora_infraestructura(self):
        """Genera un plan detallado de mejora de infraestructura"""
        plan = {
            'acciones_inmediatas': [],
            'acciones_corto_plazo': [],
            'acciones_largo_plazo': [],
            'costo_estimado': {},
            'impacto_esperado': {}
        }

        # Análisis integral
        recomendaciones = self.generar_recomendaciones_avanzadas()
        vulnerabilidades = self.analizar_vulnerabilidad_red()

        # Acciones inmediatas (urgentes)
        for prioridad in recomendaciones.get('prioridades', []):
            if prioridad['prioridad'] == 1:
                plan['acciones_inmediatas'].append({
                    'accion': prioridad['accion'],
                    'descripcion': prioridad['descripcion'],
                    'costo': 'Alto',
                    'tiempo': '1-3 meses',
                    'beneficio': 'Reducción inmediata de congestión'
                })

        # Acciones a corto plazo
        for vuln in vulnerabilidades['nodos_criticos']:
            if vuln['nivel'] == 'Crítico':
                plan['acciones_corto_plazo'].append({
                    'accion': f"Crear rutas alternativas para {vuln['nodo']}",
                    'descripcion': f"Reducir dependencia del nodo crítico {vuln['nodo']}",
                    'costo': 'Medio',
                    'tiempo': '3-6 meses',
                    'beneficio': 'Mayor robustez de la red'
                })

        # Acciones a largo plazo
        if recomendaciones.get('eficiencia_red', 0) < 0.6:
            plan['acciones_largo_plazo'].append({
                'accion': 'Rediseño parcial de la red',
                'descripcion': 'Optimizar conexiones para mejorar eficiencia general',
                'costo': 'Muy Alto',
                'tiempo': '1-2 años',
                'beneficio': 'Mejora significativa en eficiencia'
            })

        return plan

    def calcular_metricas_rendimiento(self):
        """ Calcula métricas avanzadas de rendimiento de la red"""
        metricas = {
            'throughput': 0,
            'latencia_promedio': 0,
            'utilizacion_promedio': 0,
            'indice_equilibrio': 0,
            'factor_congestion': 0
        }

        # Throughput: vehículos procesados por unidad de tiempo
        total_vehiculos = sum(self.flujo_vehicular.values())
        total_aristas = len(self.flujo_vehicular) if self.flujo_vehicular else 1
        metricas['throughput'] = total_vehiculos / max(1, total_aristas)

        # Latencia promedio: tiempo promedio de viaje
        if self.tiempos_promedio:
            tiempos_totales = []
            for tiempos_arista in self.tiempos_promedio.values():
                tiempos_totales.extend(tiempos_arista)
            metricas['latencia_promedio'] = sum(tiempos_totales) / len(tiempos_totales) if tiempos_totales else 0

        # Utilización promedio de las aristas
        utilizaciones = []
        for arista_key, flujo in self.flujo_vehicular.items():
            capacidad = self.capacidades_aristas.get(arista_key, 10)
            utilizacion = flujo / capacidad if capacidad > 0 else 0
            utilizaciones.append(utilizacion)
        metricas['utilizacion_promedio'] = sum(utilizaciones) / len(utilizaciones) if utilizaciones else 0

        # Índice de equilibrio: qué tan balanceado está el tráfico
        flujos = list(self.flujo_vehicular.values())
        if flujos:
            flujo_promedio = sum(flujos) / len(flujos)
            varianza = sum((f - flujo_promedio) ** 2 for f in flujos) / len(flujos)
            metricas['indice_equilibrio'] = 1.0 / (1.0 + varianza) if varianza > 0 else 1.0

        # Factor de congestión global
        congestion_indices = self.calcular_indice_congestion()
        if congestion_indices:
            indices = [info['indice'] for info in congestion_indices.values()]
            metricas['factor_congestion'] = sum(indices) / len(indices)

        return metricas

    def generar_reporte_ejecutivo(self):
        """ Genera un reporte ejecutivo completo para tomadores de decisiones"""
        reporte = {
            'resumen_ejecutivo': {},
            'metricas_clave': {},
            'problemas_identificados': [],
            'recomendaciones_priorizadas': [],
            'plan_inversion': {},
            'beneficios_esperados': []
        }

        # Obtener todos los análisis
        recomendaciones = self.generar_recomendaciones_avanzadas()
        vulnerabilidades = self.analizar_vulnerabilidad_red()
        metricas = self.calcular_metricas_rendimiento()
        plan_mejora = self.generar_plan_mejora_infraestructura()

        # Resumen ejecutivo
        eficiencia = recomendaciones.get('eficiencia_red', 0)
        estado_general = 'Excelente' if eficiencia > 0.8 else 'Bueno' if eficiencia > 0.6 else 'Regular' if eficiencia > 0.4 else 'Crítico'

        reporte['resumen_ejecutivo'] = {
            'estado_general': estado_general,
            'eficiencia_red': f"{eficiencia:.1%}",
            'puntos_criticos': len(recomendaciones.get('puntos_criticos', [])),
            'acciones_urgentes': len([p for p in recomendaciones.get('prioridades', []) if p['prioridad'] == 1])
        }

        # Métricas clave
        reporte['metricas_clave'] = {
            'throughput': f"{metricas['throughput']:.1f} veh/arista",
            'latencia_promedio': f"{metricas['latencia_promedio']:.1f} unidades",
            'utilizacion_red': f"{metricas['utilizacion_promedio']:.1%}",
            'factor_congestion': f"{metricas['factor_congestion']:.2f}",
            'robustez_red': f"{vulnerabilidades['robustez']:.1%}"
        }

        # Problemas identificados
        for prioridad in recomendaciones.get('prioridades', [])[:5]:  # Top 5
            reporte['problemas_identificados'].append({
                'problema': prioridad['tipo'],
                'severidad': f"Prioridad {prioridad['prioridad']}",
                'descripcion': prioridad['descripcion'],
                'impacto': prioridad.get('impacto', 'Medio')
            })

        # Recomendaciones priorizadas con costos
        for accion in plan_mejora['acciones_inmediatas'][:3]:
            reporte['recomendaciones_priorizadas'].append({
                'recomendacion': accion['accion'],
                'plazo': accion['tiempo'],
                'costo_estimado': accion['costo'],
                'beneficio': accion['beneficio']
            })

        return reporte

    def calcular_peso_ruta(self, ruta):
        """Calcula el peso total de una ruta"""
        return self.calcular_distancia_ruta(ruta)

    def bloquear_arista_temporal(self, origen, destino):
        """Bloquea temporalmente una arista y retorna su peso original"""
        nodo_origen = self.grafo.obtener_nodo(origen)
        if nodo_origen:
            for arista in nodo_origen.vecinos:
                if arista.destino.nombre == destino:
                    peso_original = arista.peso
                    arista.activa = False
                    return peso_original
        return None

    def restaurar_arista_temporal(self, origen, destino, peso_original):
        """Restaura una arista temporalmente bloqueada"""
        nodo_origen = self.grafo.obtener_nodo(origen)
        if nodo_origen and peso_original is not None:
            for arista in nodo_origen.vecinos:
                if arista.destino.nombre == destino:
                    arista.activa = True
                    arista.peso = peso_original

    def formatear_puntos_criticos(self, centralidad):
        """Formatea los puntos críticos para la visualización"""
        puntos = []
        for nodo, valor in centralidad.items():
            if valor > 0.2:  # Umbral de criticidad
                puntos.append({
                    'nodo': nodo,
                    'centralidad': valor,
                    'descripcion': f"Nodo {nodo} con centralidad {valor:.3f}",
                    'nivel': 'Alto' if valor > 0.5 else 'Medio'
                })
        return sorted(puntos, key=lambda x: x['centralidad'], reverse=True)

    def registrar_vehiculo(self, ruta_nombres):
        """Registra el paso de un vehículo por una ruta"""
        if len(ruta_nombres) < 2:
            return

        # Registrar flujo en cada arista de la ruta
        for i in range(len(ruta_nombres) - 1):
            origen = ruta_nombres[i]
            destino = ruta_nombres[i + 1]
            arista_key = (origen, destino)

            # Incrementar flujo vehicular
            self.flujo_vehicular[arista_key] += 1

            # Agregar al historial temporal
            self.historial_flujo[arista_key].append(self.flujo_vehicular[arista_key])

            # Mantener solo los últimos 20 registros para el historial
            if len(self.historial_flujo[arista_key]) > 20:
                self.historial_flujo[arista_key].pop(0)

    def obtener_estadisticas(self):
        """Obtiene estadísticas básicas del tráfico"""
        stats = {
            'total_vehiculos_procesados': sum(self.flujo_vehicular.values()),
            'total_aristas_activas': len(self.flujo_vehicular),
            'promedio_vehiculos_por_arista': 0,
            'arista_mas_usada': None
        }

        if self.flujo_vehicular:
            stats['promedio_vehiculos_por_arista'] = stats['total_vehiculos_procesados'] / stats[
                'total_aristas_activas']

            # Encontrar arista con más tráfico
            arista_max = max(self.flujo_vehicular.items(), key=lambda x: x[1])
            stats['arista_mas_usada'] = arista_max

        return stats

    def generar_recomendaciones(self):
        """Versión simplificada de recomendaciones para compatibilidad"""
        try:
            return self.generar_recomendaciones_avanzadas()
        except Exception as e:
            print(f"Error generando recomendaciones avanzadas: {e}")
            # Fallback a recomendaciones básicas
            return self.generar_recomendaciones_basicas()

    def generar_recomendaciones_basicas(self):
        """Genera recomendaciones básicas cuando falla el sistema avanzado"""
        recomendaciones = {
            'puntos_criticos': [],
            'cuellos_botella': [],
            'puntos_articulacion': [],
            'eficiencia_red': 0.5,
            'congestion': {},
            'predicciones': {},
            'prioridades': []
        }

        # Análisis básico de congestión
        if self.flujo_vehicular:
            # Encontrar aristas más congestionadas
            aristas_ordenadas = sorted(self.flujo_vehicular.items(), key=lambda x: x[1], reverse=True)

            for i, (arista_key, flujo) in enumerate(aristas_ordenadas[:5]):
                capacidad = self.capacidades_aristas.get(arista_key, 10)
                indice = flujo / capacidad

                nivel = "Crítico" if indice > 1.0 else "Alto" if indice > 0.7 else "Medio"

                recomendaciones['congestion'][arista_key] = {
                    'indice': indice,
                    'nivel': nivel,
                    'flujo': flujo,
                    'capacidad': capacidad
                }

                if nivel in ['Alto', 'Crítico']:
                    recomendaciones['prioridades'].append({
                        'prioridad': 1 if nivel == 'Crítico' else 2,
                        'tipo': f'Congestión {nivel}',
                        'descripcion': f"Arista {arista_key[0]}-{arista_key[1]} con {flujo} vehículos",
                        'accion': 'Reducir tráfico o aumentar capacidad',
                        'impacto': 'Alto'
                    })

        return recomendaciones

    def calcular_centralidad_intermediacion(self):
        """Calcula centralidad de intermediación básica"""
        try:
            return self.calcular_betweenness_centrality_optimizado()
        except:
            # Fallback simple
            centralidad = {}
            nodos = [nodo.nombre for nodo in self.grafo.nodos]

            for nodo in nodos:
                # Centralidad básica basada en número de conexiones
                nodo_obj = self.grafo.obtener_nodo(nodo)
                if nodo_obj:
                    num_conexiones = len(nodo_obj.vecinos)
                    centralidad[nodo] = num_conexiones / len(nodos) if len(nodos) > 1 else 0

            return centralidad

    def identificar_cuellos_botella(self):
        """Identifica cuellos de botella básicos"""
        cuellos_botella = []

        # Buscar aristas con alta congestión
        for arista_key, flujo in self.flujo_vehicular.items():
            capacidad = self.capacidades_aristas.get(arista_key, 10)
            if flujo > capacidad * 0.8:  # 80% de capacidad
                cuellos_botella.append({
                    'arista': arista_key,
                    'flujo': flujo,
                    'capacidad': capacidad,
                    'congestion': flujo / capacidad
                })

        return sorted(cuellos_botella, key=lambda x: x['congestion'], reverse=True)

    def analizar_conectividad(self):
        """Análisis básico de conectividad"""
        try:
            return self.encontrar_puntos_articulacion()
        except:
            # Fallback simple
            puntos_articulacion = []
            nodos = [nodo.nombre for nodo in self.grafo.nodos]

            for nodo in nodos:
                nodo_obj = self.grafo.obtener_nodo(nodo)
                if nodo_obj and len(nodo_obj.vecinos) >= 2:
                    puntos_articulacion.append({
                        'nodo': nodo,
                        'conexiones': len(nodo_obj.vecinos),
                        'importancia': 'Alta' if len(nodo_obj.vecinos) > 3 else 'Media'
                    })

            return puntos_articulacion

    def obtener_peso_arista(self, origen, destino):
        """Obtiene el peso de una arista específica"""
        nodo_origen = self.grafo.obtener_nodo(origen)
        if nodo_origen:
            for arista in nodo_origen.vecinos:
                if arista.destino.nombre == destino:
                    return arista.peso
        return float('inf')

    def encontrar_puntos_articulacion(self):
        """Implementación básica de puntos de articulación"""
        puntos = []
        nodos = [nodo.nombre for nodo in self.grafo.nodos]

        for nodo in nodos:
            nodo_obj = self.grafo.obtener_nodo(nodo)
            if nodo_obj:
                # Si un nodo tiene muchas conexiones, es potencialmente crítico
                if len(nodo_obj.vecinos) >= 3:
                    puntos.append({
                        'nodo': nodo,
                        'conexiones': len(nodo_obj.vecinos),
                        'tipo': 'Hub'
                    })

        return puntos

    def contar_componentes_conexas(self):
        """Cuenta componentes conexas básicamente"""
        # Implementación simple - asume todo conectado por ahora
        return 1

    def contar_componentes_conexas_sin_nodo(self, nodo_excluido):
        """Cuenta componentes conexas excluyendo un nodo"""
        # Implementación simple
        return 1

    def encontrar_puentes(self):
        """Encuentra puentes (aristas críticas) básico"""
        puentes = []

        # Buscar aristas que si se quitan aumentarían significativamente distancias
        for arista_key, flujo in self.flujo_vehicular.items():
            if flujo > 0:  # Si hay tráfico, es potencialmente un puente
                capacidad = self.capacidades_aristas.get(arista_key, 10)
                if flujo / capacidad > 0.9:  # Muy utilizada
                    puentes.append(arista_key)

        return puentes