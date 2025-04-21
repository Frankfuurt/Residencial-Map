# Mapa Residencial

Aplicación de visualización interactiva para un mapa residencial, que permite seleccionar propiedades y ver su información detallada. Desarrollada con Streamlit para una interfaz web moderna y reactiva.

## Características

- Visualización de casas de un residencial
- Selección interactiva de propiedades
- Panel informativo con detalles de cada propiedad
- Distinción visual entre propiedades disponibles y ocupadas

## Requisitos

- Python 3.6 o superior
- Streamlit
- Pillow (biblioteca para manejo de imágenes)

## Instalación

1. Clona este repositorio:
```
git clone <URL_del_repositorio>
cd Residencial-Map
```

2. Crea un entorno virtual (recomendado):
```
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
```

3. Instala las dependencias:
```
pip install -r requirements.txt
```

## Uso

Ejecuta la aplicación con:
```
streamlit run residencial_map_web.py --server.port=8080 --server.address=0.0.0.0 --server.enableCORS=false --server.enableXsrfProtection=false
```

Accede a la aplicación en tu navegador:
```
http://localhost:8080
```

## Funcionalidades

- **Interacción**: Selecciona cualquier casa del mapa usando el menú desplegable o el botón de selección aleatoria.
- **Panel de información**: Al seleccionar una casa, sus detalles aparecerán en el panel lateral.
- **Visualización**: Las casas ocupadas aparecen en azul claro, las disponibles en verde claro, y la seleccionada en amarillo.

## Personalización

Para agregar o modificar las propiedades, edita el archivo `houses_data.json` que contiene toda la información de las casas y su ubicación en el mapa.