# gui.py

import random
import time
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QListWidget, QLabel, QMessageBox, QScrollArea,
    QProgressBar, QHBoxLayout, QFrame, QTableWidget, QTableWidgetItem, QApplication,
    QSizePolicy, QListWidgetItem  # Añadimos QListWidgetItem aquí
)
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QHeaderView
from multiprocessing import Process, Queue
from functions import procesar_datos
from PyQt5.QtGui import QIcon


class VentanaPrincipal(QWidget):
    def __init__(self):
        super().__init__()
        self.tareas_pendientes = {}
        self.initUI()
        self.queue = Queue()
        self.procesos = {}
        self.tareas_en_progreso = {}
        self.timer = QTimer()
        self.timer.timeout.connect(self.verificar_resultados)
        
        # Inicializar el contador de tareas y la lista de tareas completadas
        self.contador_tareas = 0
        self.tareas_completadas = []

        self.ventanas_reporte = []

    def initUI(self):
        self.setWindowTitle('Sistema de Gestión de Tareas')

        # Obtener la altura de la pantalla
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        screen_height = screen_geometry.height()

        # Establecer la altura máxima de la ventana
        self.setMaximumHeight(screen_height)

        # Establecer el tamaño y posición inicial de la ventana
        self.setGeometry(100, 100, 650, 550)

        # Crear el layout principal
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(10)
        self.setLayout(self.layout)

        self.label_pendientes = QLabel('Tareas Pendientes:')
        self.layout.addWidget(self.label_pendientes)

        self.lista_pendientes = QListWidget()
        self.layout.addWidget(self.lista_pendientes)

        botones_layout = QHBoxLayout()
        botones_layout.setSpacing(10)

        self.boton_agregar = QPushButton('Agregar Tarea')
        self.boton_agregar.setIcon(QIcon("icons/add.svg")) 
        self.boton_agregar.clicked.connect(self.agregar_tarea)
        botones_layout.addWidget(self.boton_agregar)

        self.boton_procesar = QPushButton('Procesar Tareas')
        self.boton_procesar.setIcon(QIcon("icons/process.svg")) 
        self.boton_procesar.clicked.connect(self.procesar_tareas)
        botones_layout.addWidget(self.boton_procesar)

        self.boton_reporte = QPushButton('Enviar Reporte')
        self.boton_reporte.setIcon(QIcon("icons/send.svg")) 
        self.boton_reporte.clicked.connect(self.enviar_reporte)
        botones_layout.addWidget(self.boton_reporte)

        self.layout.addLayout(botones_layout)

        self.label_progreso = QLabel('Progreso de Tareas:')
        self.layout.addWidget(self.label_progreso)

        # Crear un widget contenedor para las tareas en progreso
        self.widget_progreso = QWidget()
        self.layout_progreso = QVBoxLayout()
        self.layout_progreso.setContentsMargins(0, 0, 0, 0)
        self.layout_progreso.setSpacing(0)

        self.layout_progreso.setAlignment(Qt.AlignTop)
        
        self.widget_progreso.setLayout(self.layout_progreso)

        # Crear el área de desplazamiento para las tareas en progreso
        self.scroll_progreso = QScrollArea()
        self.scroll_progreso.setWidgetResizable(True)
        self.scroll_progreso.setWidget(self.widget_progreso)

        # Establecer una altura fija para el scroll area
        self.scroll_progreso.setFixedHeight(180)  # Ajusta este valor según tus preferencias

        # Añadir el área de desplazamiento al layout principal
        self.layout.addWidget(self.scroll_progreso)

        # Actualizamos self.frame_progreso para que apunte al widget de progreso
        self.frame_progreso = self.widget_progreso

        self.label_completadas = QLabel('Resultados:')
        self.layout.addWidget(self.label_completadas)

        self.lista_completadas = QListWidget()
        self.layout.addWidget(self.lista_completadas)

    def agregar_tarea(self):
        # Incrementar el contador de tareas
        self.contador_tareas += 1
        # Asignar duración aleatoria
        duracion_total = random.randint(5, 25)
        # Clasificar la tarea
        if duracion_total <= 7:
            clasificacion = 'Corta'
        elif duracion_total <= 13:
            clasificacion = 'Mediana'
        else:
            clasificacion = 'Larga'
    
        tarea = f"Tarea {self.contador_tareas}"
        
        # Agregar a la lista de pendientes con la clasificación como visualización
        item_pendiente = QListWidgetItem(f"{tarea} ({clasificacion})")
        self.lista_pendientes.addItem(item_pendiente)
        
        # Guardar la información de la tarea utilizando el nombre sin clasificación
        self.tareas_pendientes[tarea] = {
            'duracion_total': duracion_total,
            'clasificacion': clasificacion
        }

    def verificar_resultados(self):
        while not self.queue.empty():
            mensaje = self.queue.get()
            if len(mensaje) == 3:
                tarea, progreso, tiempo_restante = mensaje
                resultado = None
                tiempo_total = None
            elif len(mensaje) == 4:
                tarea, progreso, tiempo_restante, resultado = mensaje
                tiempo_total = None
            elif len(mensaje) == 5:
                tarea, progreso, tiempo_restante, resultado, tiempo_total = mensaje
            else:
                continue

            # Actualizar la barra de progreso
            progress_bar = self.tareas_en_progreso[tarea]['progress_bar']
            clasificacion = self.tareas_en_progreso[tarea]['clasificacion']
            progress_bar.setValue(progreso)
           

            # Actualizar la etiqueta con el tiempo restante o indicar que está completada
            label_tarea = self.tareas_en_progreso[tarea]['label']
            if progreso >= 100:
                label_tarea.setText(f"{tarea} - Completada")

                progress_bar.setStyleSheet("""
                    QProgressBar::chunk {
                        background-color: #4CAF50;
                    }
                    QProgressBar {
                        border: 1px solid #4C566A;
                        border-radius: 5px;
                        text-align: center;
                        color: #ECEFF4;
                        background-color: #3B4252;
                    }
                """)
            else:
                label_tarea.setText(f"{tarea} ({clasificacion}) - Tiempo restante: {tiempo_restante}s")

            # Si hay resultado, la tarea ha terminado
            if resultado:
                self.lista_completadas.addItem(resultado)
                # Guardar la tarea completada y el tiempo que tomó
                clasificacion = self.tareas_en_progreso[tarea]['clasificacion']
                self.tareas_completadas.append({'tarea': tarea, 'tiempo': tiempo_total, 'clasificacion': clasificacion})
                # Esperar 2 segundos y eliminar la barra de progreso
                QTimer.singleShot(2000, lambda t=tarea: self.eliminar_tarea(t))

                # Terminar el proceso correspondiente
                self.procesos[tarea].join()
                del self.procesos[tarea]

        if not self.procesos:
            self.timer.stop()

   
    def enviar_reporte(self):
        if not self.tareas_completadas:
            QMessageBox.information(self, "Información", "No hay tareas completadas para generar el reporte.")
            return

        # Generar los datos del reporte
        report_data = []
        for tarea_info in self.tareas_completadas:
            tarea = tarea_info['tarea']
            tiempo = tarea_info['tiempo']
            clasificacion = tarea_info.get('clasificacion', 'N/A')
            report_data.append((tarea, f"{tiempo:.2f} s", clasificacion))

        # Limpiar las tareas completadas de la lista
        self.lista_completadas.clear()
        self.tareas_completadas.clear()
        

        nueva_ventana = VentanaReporte(report_data)
        self.ventanas_reporte.append(nueva_ventana)
        nueva_ventana.show()

    def procesar_tareas(self):
        if self.lista_pendientes.count() == 0:
            QMessageBox.information(self, "Información", "No hay tareas pendientes para procesar.")
            return

        # Procesamos cada tarea utilizando la información almacenada
        for index in range(self.lista_pendientes.count()):
            # Obtener el item y el texto mostrado
            item = self.lista_pendientes.item(index)
            texto_item = item.text()
            
            # Extraer el nombre de la tarea sin la clasificación
            tarea = texto_item.split(' (')[0]  # Esto obtiene 'Tarea X'
            
            # Recuperar la información almacenada
            tarea_info = self.tareas_pendientes.get(tarea)
            if tarea_info is None:
                continue  # Si no encontramos la tarea, pasamos a la siguiente

            duracion_total = tarea_info['duracion_total']
            clasificacion = tarea_info['clasificacion']

            # Crear y arrancar el proceso
            p = Process(target=procesar_datos, args=(tarea, self.queue, duracion_total))
            p.start()

            self.procesos[tarea] = p

            # Crear una sección para la tarea en progreso
            widget_tarea = QWidget()
            layout_tarea = QHBoxLayout()
            layout_tarea.setContentsMargins(0, 0, 0, 5)  
           
            widget_tarea.setLayout(layout_tarea)
            # Etiqueta de la tarea con tiempo restante y clasificación
            label_tarea = QLabel(f"{tarea} ({clasificacion}) - Tiempo restante: {duracion_total}s")
            layout_tarea.addWidget(label_tarea)

            # Barra de progreso
            progress_bar = QProgressBar()
            progress_bar.setObjectName("GeneralProgressBar")  # Asignamos un ID
            progress_bar.setValue(0)
            layout_tarea.addWidget(progress_bar)

            self.tareas_en_progreso[tarea] = {
                'widget': widget_tarea,
                'progress_bar': progress_bar,
                'label': label_tarea,
                'duracion_total': duracion_total,
                'clasificacion': clasificacion
            }
            self.layout_progreso.addWidget(widget_tarea)

        # Limpiar la lista de pendientes y las tareas pendientes
        self.lista_pendientes.clear()
        self.tareas_pendientes.clear()

        if not self.timer.isActive():
            self.timer.start(50)

    def eliminar_tarea(self, tarea):
        # Eliminar el widget de la tarea del layout
        widget_tarea = self.tareas_en_progreso[tarea]['widget']
        self.layout_progreso.removeWidget(widget_tarea)
        widget_tarea.setParent(None)
        del self.tareas_en_progreso[tarea]

        # Ya no es necesario actualizar la altura del scroll_progreso


class VentanaReporte(QWidget):
    def __init__(self, report_data):
        super().__init__()
        self.setWindowTitle('Reporte de Tareas Completadas')
        self.setGeometry(150, 150, 600, 400)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Etiqueta para indicar el estado actual
        self.status_label = QLabel('Generando reporte...')
        self.layout.addWidget(self.status_label)

        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.progress_bar.setValue(0)
        self.layout.addWidget(self.progress_bar)

        # Tabla para mostrar el reporte
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['Tarea', 'Tiempo Total', 'Clasificación'])
        self.table.setRowCount(0)
        self.layout.addWidget(self.table)
        self.table.verticalHeader().setVisible(False)

        # Ajustar la tabla para que ocupe todo el ancho
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Botón de cerrar, inicialmente oculto
        self.boton_cerrar = QPushButton("Cerrar")
        self.boton_cerrar.setObjectName("btnCerrar")  # Asignamos un ID
        self.boton_cerrar.setVisible(False)  # Oculto hasta que el reporte sea enviado
        self.boton_cerrar.clicked.connect(self.close)  # Cerrar la ventana al hacer clic
        self.layout.addWidget(self.boton_cerrar)

        # Configuración para el reporte
        self.report_data = report_data
        self.total_tasks = len(report_data)

        # Variables para la generación del reporte
        self.total_time = self.total_tasks * 1000  # 1 segundo por tarea
        self.elapsed_time = 0
        self.next_task_index = 0
        self.timer_interval = 1000  # Temporizador para actualizar cada segundo
        self.sending_report = False  # Variable para controlar el envío del reporte
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(self.timer_interval)

    def update_progress(self):
        if not self.sending_report:
            # Incrementar el tiempo transcurrido
            self.elapsed_time += self.timer_interval

            # Calcular el progreso de la barra
            progress = int((self.elapsed_time / self.total_time) * 100)
            if progress > 100:
                progress = 100
            self.progress_bar.setValue(progress)

            # Mostrar tareas una por una en intervalos de tiempo
            if self.next_task_index < self.total_tasks:
                tarea, tiempo, clasificacion = self.report_data[self.next_task_index]
                row_position = self.table.rowCount()
                self.table.insertRow(row_position)
                self.table.setItem(row_position, 0, QTableWidgetItem(tarea))
                self.table.setItem(row_position, 1, QTableWidgetItem(tiempo))
                self.table.setItem(row_position, 2, QTableWidgetItem(clasificacion))
                self.next_task_index += 1

            # Detener el temporizador cuando todas las tareas se han agregado
            if self.next_task_index >= self.total_tasks:
                self.sending_report = True  # Cambiar a modo de "enviando reporte"
                self.elapsed_time = 0  # Reiniciar el tiempo
                self.progress_bar.setValue(0)  # Reiniciar la barra de progreso
                self.status_label.setText('Enviando reporte...')  # Cambiar el mensaje
        else:
            # Segunda fase: "Enviando reporte"
            self.elapsed_time += self.timer_interval
            progress = int((self.elapsed_time / 4000) * 100)  # Dura 4 segundos
            if progress > 100:
                progress = 100
            self.progress_bar.setValue(progress)

            # Si han pasado 4 segundos, detener el temporizador
            if self.elapsed_time >= 4000:  # 4000 ms = 4 segundos
                self.timer.stop()
                self.progress_bar.setValue(100)
                self.status_label.setText('Reporte enviado con éxito.')

                # Mostrar el botón de cerrar después de que el reporte se haya enviado
                self.boton_cerrar.setVisible(True)
