import sys
import json
import webview
import twisted
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QFileDialog, QComboBox, QScrollArea, QTextEdit, QMessageBox
from PyQt6.QtCore import Qt

comment_status = {
    "":"",
    "Test": "Test",
    "Colgó": "Drop",
    "No contestó": "Neutral",
    "No le interesa": "Drop",
    "Inviable (Muy molesto)": "Drop",
    "Ël / Ella no toma decisiones": "Neutral",
    "Cliente molesto": "Neutral",
    "Reagendar": "Neutral",
    "Llamada efectiva": "Good"}

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.data = None
        self.filePath = None
        self.current_index = 0

        # Cargar el archivo JSON al inicio
        self.loadJSONFile()
        if not self.data:
            sys.exit(app.exit())  # Si no se seleccionó un archivo o hubo un error, cerrar el programa
        
        # Establece el size de la ventana y su posicion y la inicia
        self.setGeometry(int(1920*2/5),50, int(1920/3), 600)
        self.initUI()
        self.show()
        
    def initUI(self):
        
        # Crea ventana
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Layout principal y de la data
        main_layout = QVBoxLayout()
        data_layout = QVBoxLayout()

        self.labels = {
            "Num": QLabel(self),
            "Name": QLabel(self),
            "Fulladdress": QLabel(self),
            "Street": QLabel(self),
            "Municipality": QLabel(self),
            "Categories": QLabel(self),
            "Phone": QLabel(self),
            "Phones": QLabel(self),
            "Email": QLabel(self),
            "Social Medias": QLabel(self),
            "Review Count": QLabel(self),
            "Average Rating": QLabel(self),
            "Website": QLabel(self),
            "Opening Hours": QLabel(self),
            "Marginalization Index": QLabel(self),
            "Google Maps URL": QLabel(self),
            "Typified": QLabel(self),
            "User Comment": QLabel(self),
            "Comment Status": QLabel(self)
        }
        
        for label in self.labels.values():
            data_layout.addWidget(label)
        
        # Creas el QScrollArea y el QWidget que lo contendrá
        scroll_area = QScrollArea(self)  
        scroll_area.setFixedHeight(500)
        scroll_widget = QWidget(self)  
        scroll_widget.setLayout(data_layout)
        
        # Configura el QScrollArea
        scroll_area.setWidgetResizable(True)  # permite que el widget dentro del área de desplazamiento cambie su tamaño
        scroll_area.setWidget(scroll_widget)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        main_layout.addWidget(scroll_area)
        #main_layout.addLayout(data_layout)

        # Creando el QComboBox y añadiendo opciones
        self.comboBox = QComboBox(self)
        options = ["","Colgó" ,"No contestó" ,"No le interesa" ,"Inviable (Muy molesto)" ,"Ël / Ella no toma decisiones" ,"Cliente molesto" ,"Reagendar" ,"Llamada efectiva" ,"Cliente"]
        self.comboBox.addItems(options)
        self.comboBox.setVisible(False)  # Inicialmente, el QComboBox estará oculto

        # Botón para avanzar al objeto JSON anterior
        previous_button_layout = QHBoxLayout()
        self.previous_button = QPushButton("Anterior", self)
        self.previous_button.clicked.connect(self.show_previous_data)
        previous_button_layout.addWidget(self.previous_button)
        
        # Botón para avanzar al siguiente objeto JSON
        next_button_layout = QHBoxLayout()
        self.next_button = QPushButton("Siguiente", self)
        self.next_button.clicked.connect(self.show_next_data)
        next_button_layout.addWidget(self.next_button)
        
        # Agregar boton de Google Maps
        googleMaps_button_layout = QHBoxLayout()
        self.googleMaps_button = QPushButton("Abrir Google Maps", self)
        self.googleMaps_button.clicked.connect(self.toggle_google_maps)
        googleMaps_button_layout.addWidget(self.googleMaps_button)
        
        # Botón para agregar comentario
        comment_button_layout = QHBoxLayout()
        self.comment_button = QPushButton("Tipificado", self)
        self.comment_button.clicked.connect(self.toggle_comment_box)
        comment_button_layout.addWidget(self.comment_button)
        
        # Boton de guardado
        self.save_comment_button = QPushButton("Guardar tipificado", self)
        self.save_comment_button.clicked.connect(self.save_comment)
        comment_button_layout.addWidget(self.save_comment_button)
        
        # Añadir QTextEdit para comentario escrito
        self.comment_input = QTextEdit(self)
        
        # Conecta el signal currentTextChanged a la función update_comment_input
        self.comboBox.currentTextChanged.connect(self.update_comment_input)
        
        # Mostrar objetos en el main_layout
        main_layout.addLayout(previous_button_layout)
        main_layout.addLayout(next_button_layout)
        main_layout.addLayout(googleMaps_button_layout)
        main_layout.addLayout(comment_button_layout)
        main_layout.addWidget(self.comboBox)
        main_layout.addWidget(self.comment_input)

        self.central_widget.setLayout(main_layout)
        self.setWindowTitle('Call Center App 1.0')
        self.show_data()

    def show_data(self):
        if self.data and 0 <= self.current_index < len(self.data):
            item = self.data[self.current_index]
            for key, label in self.labels.items():
                value = item.get(key, 'NA')
                spaces = "&nbsp;" * (len(key)+10)
                formatted_value = value.replace(",", f"<br>{spaces}") if (key == "Opening Hours" or key == "Categories") and isinstance(value, str) else value
                label.setText(f"<b>{key}:</b>{formatted_value}")
            
    def show_previous_data(self):
        item = self.data[self.current_index]
        
        # Si el comentario del JSON esta vacio, entonces no podra cambiar de pestaña
        if "Typified" in item and (item["Typified"] == "" or item["Typified"] == 'NA' or item["Typified"] is None):
            self.show_error_message("Tienes que escoger un comentario y guardarlo")
            pass
        
        if not "Typified" in item:
            self.show_error_message("Tienes que escoger un comentario y guardarlo")
            pass
        else:
            # Se resta 1 al indice para la paginacion
            self.current_index -= 1

            # Si el indice es menor a la cantidad de objetos, reiniciar el índice
            if self.current_index <= len(self.data):  
                self.current_index = 0

            # Mostrar datos del objeto JSON
            self.show_data()
            
    def show_next_data(self):
        item = self.data[self.current_index]
        
        # Si el comentario del JSON esta vacio, entonces no podra cambiar de pestaña
        if "Typified" in item and (item["Typified"] == "" or item["Typified"] == 'NA' or item["Typified"] is None):
            self.show_error_message("Tienes que escoger un comentario y guardarlo")
            pass
        
        if not "Typified" in item:
            self.show_error_message("Tienes que escoger un comentario y guardarlo")
            pass
        else:
            # Se suma 1 al indice para la paginacion
            self.current_index += 1

            #Si se supera la cantidad de objetos, reiniciar el índice
            if self.current_index >= len(self.data): 
                self.current_index = 0

            # Mostrar datos del objeto JSON
            self.show_data()
    
    def toggle_google_maps(self):
        # Delimitar los indices al numero de objetos JSON y escoger el objeto JSON actual 
        if self.data and 0 <= self.current_index < len(self.data):
            item = self.data[self.current_index]
            
            # Checar si el item si esta accediendo a los datos que necesitamos  y checar que si este entrando en initUI
            try:
                webview.create_window("Google Maps", url=item["Google Maps URL"], width=int(1920/2), height=1000, x = 0, y = 0)
                webview.start()
            except:
                self.show_error_message("No se pudo accesar al URL")
                print('No se pudo accesar al URL')
                
    def toggle_comment_box(self):
        # Esta función mostrará u ocultará el QComboBox según su estado actual
        self.comboBox.setVisible(not self.comboBox.isVisible())
    
    def update_comment_input(self, selected_option):
        
        # Definimos un texto predeterminado según la opción seleccionada
        if selected_option == "No contestó":
            default_text = "Fecha y hora para reagendar:"
        elif selected_option == "Ël / Ella no toma decisiones":
            default_text = """Nombre del tomador de decisiones: \nTeléfono: \nExtension: \nCorreo: \nFecha y hora para reagendar:"""
        elif selected_option == "Cliente molesto":
            default_text = """DIRIGIR A XCIEN \nNombre: \nEmpresa: \nTeléfono: \nExtension: \nCorreo: \nProblema:"""
        elif selected_option == "Reagendar":
            default_text = "Fecha y hora para reagendar:"
        elif selected_option == "Llamada efectiva":
            default_text = """Nombre: \nEmpresa: \nTeléfono: \nExtension: \nCorreo:"""
        else:
            default_text = ""
        
        # Establece el texto predeterminado en QLineEdit
        self.comment_input.setText(default_text)
        
    def save_comment(self):
        selected_comment = self.comboBox.currentText()
        written_comment = self.comment_input.toPlainText()
        if self.data and 0 <= self.current_index < len(self.data):
            item = self.data[self.current_index]
            
            # Guarda el comentario seleccionado del ComboBox, User Comment y el Comment Status en el objeto JSON
            item["Typified"] = selected_comment  
            item["User Comment"] = written_comment 
            item["Comment Status"] = comment_status[selected_comment]
            
            # Actualiza la etiqueta de las 3 llaves directamente
            self.labels["Typified"].setText(f"<b>Typified:</b> {selected_comment}")
            self.labels["User Comment"].setText(f"<b>User Comment:</b> {written_comment}")
            self.labels["Comment Status"].setText(f"<b>Comment Status:</b> {comment_status[selected_comment]}")
            
            # Guarda el archivo JSON con el comentario añadido (opcional)
            with open(self.filePath, 'w') as file:
                json.dump(self.data, file, indent=4)
                
    def show_error_message(self, message):
        error_box = QMessageBox()
        error_box.setWindowTitle("Error")
        error_box.setText(message)
        error_box.exec()

    def loadJSONFile(self):
        filePath, _ = QFileDialog.getOpenFileName(self, "Open JSON File", "", "JSON Files (*.json);;All Files (*)")
        if filePath:
            self.filePath = filePath  # Guarda la ruta del archivo en el atributo
            with open(filePath, 'r') as file:
                try:
                    self.data = json.load(file)
                except json.JSONDecodeError:
                    # Puedes agregar un cuadro de diálogo para informar sobre el error en el archivo JSON
                    pass

app = QApplication(sys.argv)
window = App()
sys.exit(app.exec())
