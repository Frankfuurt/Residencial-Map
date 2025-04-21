import json

# Factor de escala
scale_factor = 1.12  # 12% de aumento

# Cargar el archivo JSON
with open('houses_data.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Función para escalar coordenadas
def scale_coords(coords):
    return [int(coord * scale_factor) for coord in coords]

# Escalar áreas
for area_id, area_data in data['areas'].items():
    if 'coords' in area_data:
        data['areas'][area_id]['coords'] = scale_coords(area_data['coords'])

# Escalar condominios
for condo_id, condo_data in data['condominios'].items():
    if 'coords' in condo_data:
        data['condominios'][condo_id]['coords'] = scale_coords(condo_data['coords'])

# Escalar calles
for street_id, street_data in data['calles'].items():
    if 'start' in street_data:
        data['calles'][street_id]['start'] = scale_coords(street_data['start'])
    if 'end' in street_data:
        data['calles'][street_id]['end'] = scale_coords(street_data['end'])

# Escalar layout (posiciones de casas)
for house_id, pos in data['layout'].items():
    data['layout'][house_id] = scale_coords(pos)

# Guardar el archivo modificado
with open('houses_data.json', 'w', encoding='utf-8') as file:
    json.dump(data, file, indent=2, ensure_ascii=False)

print("Mapa escalado en un 12% adicional correctamente.")