import os

def corregir_rutas_mcd():
    # Esto fuerza al script a trabajar en la carpeta donde está guardado
    ruta_actual = os.path.dirname(os.path.abspath(__file__))
    os.chdir(ruta_actual)
    
    nombre_archivo = 'index.html'
    
    print("="*40)
    print(" BUSCADOR DE RUTAS - ESTADISTICAS CMI")
    print("="*40)

    if not os.path.exists(nombre_archivo):
        print(f"❌ ERROR: No veo el archivo '{nombre_archivo}'")
        print(f"Ruta revisada: {ruta_actual}")
        os.system("pause")
        return

    with open(nombre_archivo, 'r', encoding='utf-8') as f:
        lineas = f.readlines()

    reemplazos = {
        'febrero/': 'FEBRERO/',
        'marzo/':   'MARZO/',
        'abril/':   'ABRIL/'
    }

    nuevo_contenido = []
    cambios_realizados = 0

    print(f"Analizando {nombre_archivo}...\n")

    for i, linea in enumerate(lineas):
        linea_original = linea
        nueva_linea = linea
        
        for minus, MAYUS in reemplazos.items():
            if minus in nueva_linea:
                nueva_linea = nueva_linea.replace(minus, MAYUS)
        
        if nueva_linea != linea_original:
            print(f"📍 Línea {i+1} corregida:")
            print(f"   ANTES: {linea_original.strip()}")
            print(f"   AHORA: {nueva_linea.strip()}\n")
            cambios_realizados += 1
            nuevo_contenido.append(nueva_linea)
        else:
            nuevo_contenido.append(linea_original)

    if cambios_realizados > 0:
        with open(nombre_archivo, 'w', encoding='utf-8') as f:
            f.writelines(nuevo_contenido)
        print("="*40)
        print(f"✨ PROCESO TERMINADO: {cambios_realizados} líneas actualizadas.")
        print("="*40)
    else:
        print("⚠️ No se encontraron rutas en minúsculas para corregir.")
        print("Revisa si los nombres ya estaban en MAYÚSCULAS.")

    print("\nPresiona cualquier tecla para cerrar esta ventana...")
    os.system("pause > nul")

if __name__ == "__main__":
    corregir_rutas_mcd()