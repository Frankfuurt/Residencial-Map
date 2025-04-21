import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import json

class ResidencialMap:
    def __init__(self, root):
        self.root = root
        self.root.title("Mapa Residencial")
        self.root.geometry("1500x900")  # Increased window size
        self.root.attributes('-topmost', True)
        self.root.update()
        self.root.attributes('-topmost', False)
        
        print("Iniciando aplicación de Mapa Residencial...")
        
        # Variables
        self.selected_house = None
        self.houses = {}
        self.layout = {}
        self.areas = {}
        self.condominios = {}
        self.calles = {}
        
        # Cargar datos desde el archivo JSON
        self.load_house_data()
        
        # Crear el área del mapa
        self.create_map_area()
        
        # Panel de información
        self.create_info_panel()
        
        print("Aplicación iniciada correctamente.")
        
    def load_house_data(self):
        try:
            print("Cargando datos desde houses_data.json...")
            with open('houses_data.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
                self.houses = data['houses']
                self.layout = data.get('layout', {})
                self.areas = data.get('areas', {})
                self.condominios = data.get('condominios', {})
                self.calles = data.get('calles', {})
                print("Datos cargados correctamente")
        except Exception as e:
            print(f"Error al cargar datos: {str(e)}")
            messagebox.showerror("Error", f"No se pudo cargar los datos: {str(e)}")
    
    def create_map_area(self):
        # Frame principal con scrollbars
        self.map_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.map_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbars
        h_scroll = tk.Scrollbar(self.map_frame, orient=tk.HORIZONTAL)
        v_scroll = tk.Scrollbar(self.map_frame, orient=tk.VERTICAL)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Canvas con scrollbars
        self.canvas = tk.Canvas(self.map_frame, bg="#ffffff",
                              width=1500, height=900,
                              xscrollcommand=h_scroll.set,
                              yscrollcommand=v_scroll.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configurar scrollbars
        h_scroll.config(command=self.canvas.xview)
        v_scroll.config(command=self.canvas.yview)
        
        # Habilitar zoom con la rueda del mouse
        self.canvas.bind('<MouseWheel>', self.zoom)
        
        # Dibujar el mapa
        self.draw_map()
    
    def zoom(self, event):
        # Zoom in/out con la rueda del mouse
        scale = 1.1 if event.delta > 0 else 0.9
        self.canvas.scale("all", event.x, event.y, scale, scale)
    
    def draw_map(self):
        # Limpiar el canvas
        self.canvas.delete("all")
        
        # Establecer la región scrollable
        self.canvas.configure(scrollregion=(0, 0, 1500, 900))
        
        # Dibujar calles
        for calle_id, calle_data in self.calles.items():
            start = calle_data['start']
            end = calle_data['end']
            width = calle_data.get('width', 30)
            
            # Dibujar la calle
            self.canvas.create_line(
                start[0], start[1], end[0], end[1],
                width=width, fill='#808080',
                capstyle=tk.ROUND,
                tags=('calle', calle_id)
            )
            
            # Agregar nombre de la calle
            text_x = (start[0] + end[0]) / 2
            text_y = (start[1] + end[1]) / 2
            self.canvas.create_text(
                text_x, text_y,
                text=calle_data['id'],
                fill='white',
                font=('Arial', 10, 'bold'),
                tags=('calle_label', calle_id)
            )
        
        # Dibujar áreas (alberca y parque)
        for area_id, area_data in self.areas.items():
            coords = area_data['coords']
            color = '#00CED1' if area_data['tipo'] == 'alberca_pergola' else '#90EE90'
            
            self.canvas.create_rectangle(
                coords[0], coords[1], coords[2], coords[3],
                fill=color, outline='black',
                width=2,
                tags=(area_id, 'area')
            )
            
            # Agregar etiqueta del área
            center_x = (coords[0] + coords[2]) / 2
            center_y = (coords[1] + coords[3]) / 2
            self.canvas.create_text(
                center_x, center_y,
                text=area_data['descripcion'],
                font=('Arial', 12, 'bold'),
                tags=(f"{area_id}_label", 'area_label')
            )
        
        # Dibujar condominios
        for condo_id, condo_data in self.condominios.items():
            coords = condo_data['coords']
            
            self.canvas.create_rectangle(
                coords[0], coords[1], coords[2], coords[3],
                fill='#F5F5F5',
                outline='black',
                width=2,
                tags=(condo_id, 'condominio')
            )
            
            # Agregar etiqueta del condominio
            center_x = (coords[0] + coords[2]) / 2
            center_y = (coords[1] + coords[3]) / 2
            self.canvas.create_text(
                center_x, center_y,
                text=condo_data['descripcion'],
                font=('Arial', 11),
                tags=(f"{condo_id}_label", 'condo_label')
            )
            
            # Dibujar número de casas
            self.canvas.create_text(
                center_x, center_y + 20,
                text=f"{condo_data['casas']} casas",
                font=('Arial', 10),
                fill='#666666',
                tags=(f"{condo_id}_houses", 'condo_houses')
            )
        
        # Configurar eventos
        self.canvas.tag_bind('condominio', '<Button-1>', self.show_condo_info)
        self.canvas.tag_bind('area', '<Button-1>', self.show_area_info)
    
    def show_condo_info(self, event):
        # Obtener el condominio clickeado
        clicked_items = self.canvas.find_withtag('current')
        tags = self.canvas.gettags(clicked_items[0])
        for tag in tags:
            if tag in self.condominios:
                condo_data = self.condominios[tag]
                info = f"Condominio: {condo_data['descripcion']}\n"
                info += f"Número de casas: {condo_data['casas']}\n"
                info += f"Orientación: {condo_data['orientacion']}"
                
                self.update_info_panel_general("Información del Condominio", info)
                break
    
    def show_area_info(self, event):
        # Obtener el área clickeada
        clicked_items = self.canvas.find_withtag('current')
        tags = self.canvas.gettags(clicked_items[0])
        for tag in tags:
            if tag in self.areas:
                area_data = self.areas[tag]
                info = f"Área: {area_data['descripcion']}\n"
                info += f"Tipo: {area_data['tipo']}"
                
                self.update_info_panel_general("Información del Área", info)
                break

    def create_info_panel(self):
        """Crear el panel lateral para mostrar información detallada"""
        self.info_frame = tk.Frame(self.root, bg="#e0e0e0", width=300)
        self.info_frame.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.info_frame.pack_propagate(False)
        
        # Título del panel
        self.info_title = tk.Label(self.info_frame, 
            text="Información", 
            font=("Arial", 14, "bold"), 
            bg="#e0e0e0")
        self.info_title.pack(pady=20)
        
        # Contenido
        self.info_content = tk.Label(self.info_frame,
            text="Haga clic en un elemento del mapa\npara ver su información",
            font=("Arial", 11),
            bg="#e0e0e0",
            justify=tk.LEFT,
            wraplength=250)
        self.info_content.pack(padx=20, pady=10)
    
    def update_info_panel_general(self, title, content):
        self.info_title.config(text=title)
        self.info_content.config(text=content)

if __name__ == "__main__":
    root = tk.Tk()
    app = ResidencialMap(root)
    root.mainloop()