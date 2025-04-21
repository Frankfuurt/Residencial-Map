import streamlit as st
import streamlit.components.v1 as components
import json
from PIL import Image, ImageDraw, ImageFont
import io
import base64

class ResidencialMap:
    def __init__(self):
        st.set_page_config(page_title="Mapa Residencial", layout="wide")
        st.title("Mapa Residencial")
        
        # Variables
        self.houses = {}
        self.layout = {}
        self.areas = {}
        self.condominios = {}
        self.calles = {}
        
        # Configurar fuente para dibujar texto
        try:
            self.font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 14)
        except:
            self.font = ImageFont.load_default()
        
        # Inicializar estado de Streamlit si no existe
        if 'selected_condo' not in st.session_state:
            st.session_state.selected_condo = None
        if 'selected_house' not in st.session_state:
            st.session_state.selected_house = None
        if 'show_details' not in st.session_state:
            st.session_state.show_details = False
        
        # Dimensiones del mapa
        self.map_width = 1050  # Reducido de 1500
        self.map_height = 630  # Reducido de 900
        
        # Cargar datos
        self.load_house_data()
        
        # Crear layout
        self.create_layout()
    
    def load_house_data(self):
        try:
            with open('houses_data.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
                self.houses = data.get('houses', {})
                self.layout = data.get('layout', {})
                self.areas = data.get('areas', {})
                self.condominios = data.get('condominios', {})
                self.calles = data.get('calles', {})
        except Exception as e:
            st.error(f"Error al cargar los datos: {str(e)}")
    
    def create_layout(self):
        # Crear dos columnas: mapa y panel de información
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Área del mapa
            st.subheader("Mapa del Residencial")
            self.draw_map()
        
        with col2:
            # Panel de información
            st.subheader("Información")
            self.create_info_panel()
    
    def draw_map(self):
        # Crear una imagen en blanco con el nuevo tamaño
        img = Image.new('RGB', (self.map_width, self.map_height), 'white')
        draw = ImageDraw.Draw(img)
        
        # Factor de escala para ajustar todas las coordenadas
        scale_x = self.map_width / 1500
        scale_y = self.map_height / 900
        
        # Dibujar áreas primero (fondo)
        for area_id, area in self.areas.items():
            coords = area['coords']
            color = '#00CED1' if area['tipo'] == 'alberca_pergola' else '#90EE90'
            
            draw.rectangle(
                [
                    (int(coords[0] * scale_x), int(coords[1] * scale_y)),
                    (int(coords[2] * scale_x), int(coords[3] * scale_y))
                ],
                fill=color,
                outline='black'
            )
            
            # Etiqueta del área
            center_x = int((coords[0] + coords[2]) * scale_x / 2)
            center_y = int((coords[1] + coords[3]) * scale_y / 2)
            draw.text((center_x, center_y), area['descripcion'], fill='black', font=self.font, anchor="mm")
        
        # Generar mapa de áreas para hover
        hover_map = {}
        
        # Dibujar condominios
        for condo_id, condo in self.condominios.items():
            coords = condo['coords']
            # Agregar coordenadas al mapa de hover con escala
            hover_map[condo_id] = {
                'coords': [
                    int(coords[0] * scale_x),
                    int(coords[1] * scale_y),
                    int(coords[2] * scale_x),
                    int(coords[3] * scale_y)
                ],
                'descripcion': f"Condominio {condo_id.split('_')[1].upper()}"
            }
            
            draw.rectangle(
                [
                    (int(coords[0] * scale_x), int(coords[1] * scale_y)),
                    (int(coords[2] * scale_x), int(coords[3] * scale_y))
                ],
                fill='#F5F5F5',
                outline='black'
            )
            
            # Pasar los factores de escala al método de dibujo de casas
            self.draw_houses_in_condominio(draw, condo, condo_id, scale_x, scale_y)

        # Dibujar las líneas de las calles
        for calle_id, calle in self.calles.items():
            draw.line(
                [
                    (int(calle['start'][0] * scale_x), int(calle['start'][1] * scale_y)),
                    (int(calle['end'][0] * scale_x), int(calle['end'][1] * scale_y))
                ],
                fill='gray',
                width=int(calle.get('width', 30) * scale_x)
            )

        # Dibujar las etiquetas de las calles al final (por encima de todo)
        for calle_id, calle in self.calles.items():
            # Calcular posición del texto
            text_x = int((calle['start'][0] + calle['end'][0]) * scale_x / 2)
            text_y = int((calle['start'][1] + calle['end'][1]) * scale_y / 2)

            # Crear una imagen temporal para el texto que podamos rotar
            if calle_id in ['calle_chaca', 'calle_cacao', 'calle_chacte', 'calle_eucalipto_vertical']:
                # Para calles verticales
                text_width = 250
                text_height = 50
                text_img = Image.new('RGBA', (text_width, text_height), (0, 0, 0, 0))
                text_draw = ImageDraw.Draw(text_img)
                
                # Dibujar el texto centrado en la imagen temporal
                text_draw.text(
                    (text_width//2, text_height//2),
                    calle['id'],
                    fill='white',
                    font=self.font,
                    anchor="mm"
                )
                
                # Rotar -90 grados (sentido horario)
                text_img = text_img.rotate(-90, expand=True, fillcolor=(0,0,0,0))
                
                # Calcular punto medio vertical del segmento de calle
                start_y = int(calle['start'][1] * scale_y)
                end_y = int(calle['end'][1] * scale_y)
                mid_y = (start_y + end_y) // 2
                
                # Ajustar posiciones específicas para cada calle vertical
                if calle_id == 'calle_chaca':
                    x_offset = -text_height//2
                    y_offset = -text_width//2
                elif calle_id == 'calle_cacao':
                    x_offset = -text_height//2
                    y_offset = -text_width//2
                elif calle_id == 'calle_eucalipto_vertical':
                    x_offset = -text_height//2
                    y_offset = -text_width//2 - 30  # Ajustado para mejor visibilidad en la parte inferior del mapa
                else:  # calle_chacte
                    x_offset = -text_height//2
                    y_offset = -text_width//2
                
                # Calcular posición final
                text_pos = (
                    int(text_x + x_offset), 
                    int(mid_y + y_offset)
                )
                
                # Pegar la imagen rotada usando máscara alfa
                img.paste(text_img, text_pos, text_img)
            else:
                # Para calles horizontales
                # Calcular punto medio horizontal del segmento de calle
                mid_x = (int(calle['start'][0] * scale_x) + int(calle['end'][0] * scale_x)) // 2
                
                # Ajustes específicos por calle
                y_offsets = {
                    'calle_zapote': -2,
                    'calle_jabin': -2,
                    'calle_caoba': -2,
                    'av_paseo': -2,
                }
                y_offset = y_offsets.get(calle_id, 0)
                
                draw.text(
                    (mid_x, text_y + y_offset),
                    calle['id'],
                    fill='white',
                    font=self.font,
                    anchor="mm"
                )
        
        # Convertir la imagen a base64
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_b64 = base64.b64encode(img_bytes.getvalue()).decode()
        
        # Crear HTML con interactividad
        html = f"""
        <div style="position: relative; width: {self.map_width}px; height: {self.map_height}px;">
            <img src="data:image/png;base64,{img_b64}" style="width: 100%; height: 100%;" />
            <div id="hover-label" style="position: absolute; display: none; background: rgba(0,0,0,0.7); color: white; padding: 5px; border-radius: 3px; pointer-events: none;"></div>
        </div>
        <script>
            const hoverMap = {json.dumps(hover_map)};
            const container = document.querySelector('div');
            const label = document.getElementById('hover-label');
            
            container.addEventListener('mousemove', (e) => {{
                const rect = container.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                // Escalar coordenadas según el tamaño actual de la imagen
                const scaleX = {self.map_width} / container.offsetWidth;
                const scaleY = {self.map_height} / container.offsetHeight;
                const mapX = x * scaleX;
                const mapY = y * scaleY;
                
                let found = false;
                for (const [id, data] of Object.entries(hoverMap)) {{
                    const coords = data.coords;
                    if (mapX >= coords[0] && mapX <= coords[2] && 
                        mapY >= coords[1] && mapY <= coords[3]) {{
                        label.textContent = data.descripcion;
                        label.style.display = 'block';
                        label.style.left = `${{e.clientX - rect.left + 10}}px`;
                        label.style.top = `${{e.clientY - rect.top + 10}}px`;
                        found = true;
                        break;
                    }}
                }}
                
                if (!found) {{
                    label.style.display = 'none';
                }}
            }});
            
            container.addEventListener('mouseleave', () => {{
                label.style.display = 'none';
            }});
        </script>
        """
        
        # Mostrar el mapa interactivo usando un componente HTML
        components.html(html, height=self.map_height, scrolling=False)
    
    def draw_houses_in_condominio(self, draw, condo, condo_id, scale_x, scale_y):
        coords = condo['coords']
        num_houses = condo['casas']
        orientation = condo['orientacion']
        
        # Aplicar escala a las coordenadas del condominio
        scaled_coords = [
            int(coords[0] * scale_x),
            int(coords[1] * scale_y),
            int(coords[2] * scale_x),
            int(coords[3] * scale_y)
        ]
        
        if orientation == "Horizontal":
            # Para condominios horizontales con dos filas
            if condo_id in ['eucalipto_1', 'eucalipto_2', 'eucalipto_6']:
                houses_per_row = num_houses // 2
                house_width = (scaled_coords[2] - scaled_coords[0]) / (houses_per_row + 1)
                total_height = scaled_coords[3] - scaled_coords[1]
                house_height = total_height / 4
                
                for row in range(2):
                    y_offset = scaled_coords[1] + (total_height * (row + 1)) / 3
                    
                    for i in range(houses_per_row):
                        x = scaled_coords[0] + ((i + 1) * house_width)
                        y = y_offset
                        
                        house_number = i + 1 + (row * houses_per_row)
                        house_id = f"{condo_id}-{house_number:02d}"
                        is_selected = (st.session_state.selected_condo == condo_id and 
                                    st.session_state.selected_house == house_id)
                        
                        fill_color = 'yellow' if is_selected else '#F5F5F5'
                        
                        draw.rectangle(
                            [
                                (int(x - house_width/2), int(y - house_height/2)),
                                (int(x + house_width/2), int(y + house_height/2))
                            ],
                            fill=fill_color,
                            outline='black'
                        )
                        
                        draw.text((x, y), str(house_number), fill='black', font=self.font, anchor="mm")
            else:
                house_width = (scaled_coords[2] - scaled_coords[0]) / (num_houses + 1)
                house_height = (scaled_coords[3] - scaled_coords[1]) / 3
                
                for i in range(num_houses):
                    x = scaled_coords[0] + ((i + 1) * house_width)
                    y = scaled_coords[1] + ((scaled_coords[3] - scaled_coords[1]) / 2)
                    
                    house_id = f"{condo_id}-{i+1:02d}"
                    is_selected = (st.session_state.selected_condo == condo_id and 
                                st.session_state.selected_house == house_id)
                    
                    fill_color = 'yellow' if is_selected else '#F5F5F5'
                    
                    draw.rectangle(
                        [
                            (int(x - house_width/2), int(y - house_height/2)),
                            (int(x + house_width/2), int(y + house_height/2))
                        ],
                        fill=fill_color,
                        outline='black'
                    )
                    
                    draw.text((x, y), str(i+1), fill='black', font=self.font, anchor="mm")
                
        else:  # Vertical
            if condo_id == 'eucalipto_4':
                houses_per_col = num_houses // 2
                total_width = scaled_coords[2] - scaled_coords[0]
                house_width = total_width / 4
                house_height = (scaled_coords[3] - scaled_coords[1]) / (houses_per_col + 1)
                
                for col in range(2):
                    x_offset = scaled_coords[0] + (total_width * (col + 1)) / 3
                    
                    for i in range(houses_per_col):
                        x = x_offset
                        y = scaled_coords[1] + ((i + 1) * house_height)
                        
                        house_number = i + 1 + (col * houses_per_col)
                        house_id = f"{condo_id}-{house_number:02d}"
                        is_selected = (st.session_state.selected_condo == condo_id and 
                                    st.session_state.selected_house == house_id)
                        
                        fill_color = 'yellow' if is_selected else '#F5F5F5'
                        
                        draw.rectangle(
                            [
                                (int(x - house_width/2), int(y - house_height/2)),
                                (int(x + house_width/2), int(y + house_height/2))
                            ],
                            fill=fill_color,
                            outline='black'
                        )
                        
                        draw.text((x, y), str(house_number), fill='black', font=self.font, anchor="mm")
            else:
                house_width = (scaled_coords[2] - scaled_coords[0]) / 3
                house_height = (scaled_coords[3] - scaled_coords[1]) / (num_houses + 1)
                
                for i in range(num_houses):
                    x = scaled_coords[0] + ((scaled_coords[2] - scaled_coords[0]) / 2)
                    y = scaled_coords[1] + ((i + 1) * house_height)
                    
                    house_id = f"{condo_id}-{i+1:02d}"
                    is_selected = (st.session_state.selected_condo == condo_id and 
                                st.session_state.selected_house == house_id)
                    
                    fill_color = 'yellow' if is_selected else '#F5F5F5'
                    
                    draw.rectangle(
                        [
                            (int(x - house_width/2), int(y - house_height/2)),
                            (int(x + house_width/2), int(y + house_height/2))
                        ],
                        fill=fill_color,
                        outline='black'
                    )
                    
                    draw.text((x, y), str(i+1), fill='black', font=self.font, anchor="mm")
    
    def create_info_panel(self):
        # Lista desplegable de condominios
        condo_names = list(self.condominios.keys())
        selected_condo = st.selectbox(
            "Seleccionar Condominio",
            condo_names,
            format_func=lambda x: self.condominios[x]['descripcion'],
            key='condo_selector'
        )
        
        if selected_condo:
            st.session_state.selected_condo = selected_condo
            condo = self.condominios[selected_condo]
            
            # Generar lista de casas en el condominio
            house_ids = [f"{selected_condo}-{i+1:02d}" for i in range(condo['casas'])]
            selected_house = st.selectbox(
                "Seleccionar Casa",
                house_ids,
                format_func=lambda x: f"Casa {int(x.split('-')[1])}",
                key='house_selector'
            )
            
            if selected_house:
                st.session_state.selected_house = selected_house
                
                # Botón para mostrar detalles
                if st.button("Ver Detalles de la Casa"):
                    st.session_state.show_details = True
                
                # Mostrar información de la casa solo si se presionó el botón
                if st.session_state.show_details and st.session_state.selected_house == selected_house:
                    st.write("### Detalles de la Casa")
                    if selected_house in self.houses:
                        house = self.houses[selected_house]
                        st.write(f"**ID:** {selected_house}")
                        st.write(f"**Dirección:** {house['direccion']}")
                        st.write(f"**Estado:** {house['estado']}")
                        if 'propietario' in house:
                            st.write(f"**Propietario:** {house['propietario']}")
                        if 'tamano' in house:
                            st.write(f"**Tamaño:** {house['tamano']}")
                    else:
                        st.write("No hay información detallada disponible para esta casa")
                    
                    # Botón para ocultar detalles
                    if st.button("Ocultar Detalles"):
                        st.session_state.show_details = False
                        st.experimental_rerun()

if __name__ == "__main__":
    app = ResidencialMap()