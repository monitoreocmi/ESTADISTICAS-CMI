import os
import hashlib

def calcular_hash(ruta_archivo):
    """Genera un código único basado en el contenido del archivo."""
    hash_md5 = hashlib.md5()
    try:
        with open(ruta_archivo, "rb") as f:
            # Leemos en trozos para no saturar la memoria RAM
            for trozo in iter(lambda: f.read(4096), b""):
                hash_md5.update(trozo)
        return hash_md5.hexdigest()
    except Exception as e:
        print(f"❌ Error leyendo {ruta_archivo}: {e}")
        return None

def eliminar_duplicados():
    ruta_raiz = os.path.dirname(os.path.abspath(__file__))
    hashes_encontrados = {} # Diccionario para guardar {hash: ruta_del_archivo}
    contador_borrados = 0
    espacio_liberado = 0

    print("="*60)
    print("🚀 BUSCANDO Y ELIMINANDO FOTOS DUPLICADAS (POR CONTENIDO)")
    print("="*60)

    for raiz, _, archivos in os.walk(ruta_raiz):
        for nombre_archivo in archivos:
            # Solo procesamos imágenes
            if nombre_archivo.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                ruta_completa = os.path.join(raiz, nombre_archivo)
                
                # Obtenemos el "ADN" del archivo
                archivo_hash = calcular_hash(ruta_completa)
                
                if archivo_hash:
                    if archivo_hash in hashes_encontrados:
                        # ¡DUPLICADO DETECTADO!
                        try:
                            tamano = os.path.getsize(ruta_completa)
                            os.remove(ruta_completa)
                            print(f"🗑️  Borrando duplicado: {nombre_archivo}")
                            print(f"    (Es igual a: {os.path.basename(hashes_encontrados[archivo_hash])})")
                            contador_borrados += 1
                            espacio_liberado += tamano
                        except Exception as e:
                            print(f"⚠️  No se pudo borrar {nombre_archivo}: {e}")
                    else:
                        # Es la primera vez que vemos esta foto, la registramos
                        hashes_encontrados[archivo_hash] = ruta_completa

    print("\n" + "="*60)
    print(f"✅ PROCESO FINALIZADO")
    print(f"📸 Fotos duplicadas eliminadas: {contador_borrados}")
    print(f"💾 Espacio liberado: {round(espacio_liberado / (1024*1024), 2)} MB")
    print("="*60)

if __name__ == "__main__":
    eliminar_duplicados()
    input("\nPresiona ENTER para salir...")