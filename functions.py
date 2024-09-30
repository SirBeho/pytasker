import time
import random
import math


def procesar_datos(tarea, queue, duracion_total):
    """Simula el procesamiento de datos con una duración específica."""
    print(f"Procesando datos para {tarea}... (tardará aproximadamente {duracion_total} segundos)")
    inicio = time.time()
    # Definimos el intervalo de actualización
    update_interval = 0.1  # Actualizamos cada 0.1 segundos
    steps = int(duracion_total / update_interval)
    for i in range(steps):
        time.sleep(update_interval)
        progreso = int(((i + 1) / steps) * 100)
        tiempo_transcurrido = (i + 1) * update_interval
        tiempo_restante = max(0, math.ceil(duracion_total - tiempo_transcurrido))
        # Enviamos el progreso y el tiempo restante
        queue.put((tarea, progreso, tiempo_restante))
    fin = time.time()
    tiempo_total = fin - inicio
    resultado = f"{tarea} completada"
    queue.put((tarea, 100, 0, resultado, tiempo_total))
