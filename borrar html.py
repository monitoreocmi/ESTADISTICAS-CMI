import os
import sys

def borrar_htmls():
    # Obtiene la ruta donde está el script
    ruta_raiz = os.path.dirname(os.path.abspath(__file__))
    
    # Encabezado para el CMD
    print("\n" + "="*60)
    print("🧹 LIMPIADOR DE ARCHIVOS HTML - SISTEMA LUXOR")
    print("="*60)
    print(f"📁 Buscando en: {ruta_raiz}\n")

    contador = 0
    
    # Recorrer todas las carpetas y subcarpetas
    for carpeta_actual, subcarpetas, archivos in os.walk(ruta_raiz):
        for archivo in archivos:
            # Filtro estricto para archivos .html
            if archivo.lower().endswith(".html"):
                ruta_completa = os.path.join(carpeta_actual, archivo)
                
                # Obtener la ruta relativa para que se vea más limpio en el CMD
                ruta_relativa = os.path.relpath(ruta_completa, ruta_raiz)
                
                try:
                    os.remove(ruta_completa)
                    print(f"  [ELIMINADO] -> {ruta_relativa}")
                    contador += 1
                except Exception as e:
                    print(f"  [ERROR] No se pudo borrar {ruta_relativa}: {e}")

    # Resumen final
    print("\n" + "="*60)
    if contador > 0:
        print(f"✅ PROCESO TERMINADO CON ÉXITO")
        print(f"📊 Total de archivos borrados: {contador}")
    else:
        print("ℹ️ No se encontraron archivos HTML para limpiar.")
    print("="*60)
    
    # Pausa para que no se cierre el CMD solo
    input("\nPresiona ENTER para salir...")

if __name__ == "__main__":
    borrar_htmls()