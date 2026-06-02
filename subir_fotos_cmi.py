import time
import requests
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- CONFIGURACIÓN ---
# Usamos 'r' al principio para que las barras invertidas de Windows no den error
CARPETA_VIGILADA = r"C:\Users\Admin\Desktop\ESTADISTICAS CMI\fotos"
URL_API_FLASK = "http://127.0.0.1:5006/api/subir_foto"

class ManejadorEventos(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            # Filtro corregido para incluir .bmp y evitar errores de extensión
            ext = os.path.splitext(event.src_path)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.bmp']:
                print(f"📸 Nueva foto detectada: {os.path.basename(event.src_path)}")
                
                # Sistema de reintentos: Asegurar que iVMS soltó el archivo
                exito = False
                for i in range(5):
                    try:
                        time.sleep(1) # Espera breve
                        with open(event.src_path, 'rb'):
                            exito = True
                            break
                    except IOError:
                        print(f"⏳ Archivo bloqueado por iVMS, reintentando ({i+1}/5)...")
                
                if exito:
                    try:
                        with open(event.src_path, 'rb') as f:
                            files = {'foto': f}
                            data = {'filename': os.path.basename(event.src_path)}
                            response = requests.post(URL_API_FLASK, files=files, data=data)
                            
                            if response.status_code == 200:
                                print("✅ Foto enviada correctamente al servidor.")
                            else:
                                print(f"❌ Error al enviar al servidor: {response.text}")
                    except Exception as e:
                        print(f"❌ Error al procesar el archivo: {e}")
                else:
                    print("❌ No se pudo leer el archivo tras varios intentos.")
            else:
                print(f"🔍 Archivo ignorado (no es imagen): {os.path.basename(event.src_path)}")

if __name__ == "__main__":
    if not os.path.exists(CARPETA_VIGILADA):
        print(f"❌ ERROR: La carpeta {CARPETA_VIGILADA} no existe. Revisa la ruta.")
    else:
        print(f"👁️ Vigilando: {CARPETA_VIGILADA}")
        observer = Observer()
        # 'recursive=True' para entrar en las subcarpetas creadas por iVMS
        observer.schedule(ManejadorEventos(), CARPETA_VIGILADA, recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()