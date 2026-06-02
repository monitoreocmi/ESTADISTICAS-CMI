import os
import math
import json
import threading
import time
import shutil
import re
from datetime import datetime
from flask import Flask, render_template, abort, url_for, request, redirect, flash, send_from_directory, jsonify
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Librerías para la automatización de WhatsApp
import pyperclip
from PIL import Image
import io
import win32clipboard

# Configuración: Usamos la ruta absoluta del directorio actual
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=BASE_DIR, static_url_path='')
app.secret_key = 'luxor_fiscalizacion_fiscalizacion_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

# --- RUTA DEFINITIVA PARA LAS FOTOS ---
CARPETA_CAPTURAS = r"C:\Users\Admin\Desktop\FISCALIZACION\fotos_incidencias"

MONITORISTAS_FILE = os.path.join(BASE_DIR, "monitoristas.txt")
TURNOS_FILE = os.path.join(BASE_DIR, "turnos.txt")

# --- FUNCIONES AUXILIARES PARA ARCHIVOS TXT ---
def leer_archivo_txt(ruta_archivo):
    """Lee las líneas de un archivo txt, elimina espacios y las devuelve ordenadas."""
    if not os.path.exists(ruta_archivo):
        return []
    with open(ruta_archivo, "r", encoding="utf-8") as f:
        return sorted([line.strip().upper() for line in f if line.strip()])

def guardar_linea_txt(ruta_archivo, nueva_linea):
    """Guarda una nueva línea en el archivo txt si no existe previamente."""
    lineas = leer_archivo_txt(ruta_archivo)
    if nueva_linea.upper() not in lineas:
        with open(ruta_archivo, "a", encoding="utf-8") as f:
            f.write(nueva_linea.upper() + "\n")
        return True
    return False

# --- LÓGICA DE AUTOMATIZACIÓN DE WHATSAPP ---
def copiar_imagen_al_portapapeles(ruta_img):
    try:
        image = Image.open(ruta_img)
        output = io.BytesIO()
        image.convert("RGB").save(output, "BMP")
        data = output.getvalue()[14:]
        output.close()
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        win32clipboard.CloseClipboard()
        return True
    except Exception as e:
        print(f"Error al copiar: {e}")
        return False

# --- RUTAS DE LA API ---

# API PARA GESTIÓN DE MONITORISTAS
@app.route('/api/monitoristas', methods=['GET'])
def get_monitoristas():
    return jsonify(leer_archivo_txt(MONITORISTAS_FILE))

@app.route('/api/monitoristas', methods=['POST'])
def add_monitorista():
    data = request.get_json() or {}
    nombre = data.get('nombre', '').strip()
    if not nombre:
        return jsonify({"success": False, "msg": "Nombre inválido"}), 400
    if guardar_linea_txt(MONITORISTAS_FILE, nombre):
        return jsonify({"success": True})
    return jsonify({"success": False, "msg": "El monitorista ya existe en el archivo."})

# API PARA GESTIÓN DE TURNOS
@app.route('/api/turnos', methods=['GET'])
def get_turnos():
    return jsonify(leer_archivo_txt(TURNOS_FILE))

@app.route('/api/turnos', methods=['POST'])
def add_turno():
    data = request.get_json() or {}
    nombre = data.get('nombre', '').strip()
    if not nombre:
        return jsonify({"success": False, "msg": "Turno inválido"}), 400
    if guardar_linea_txt(TURNOS_FILE, nombre):
        return jsonify({"success": True})
    return jsonify({"success": False, "msg": "El turno ya existe en el archivo."})


@app.route('/api/preparar_whatsapp', methods=['POST'])
def preparar_whatsapp():
    if request.content_type and request.content_type.startswith('multipart/form-data'):
        if 'foto' not in request.files: 
            return jsonify({"success": False, "msg": "No hay archivo seleccionado"})
        foto = request.files['foto']
        ruta_temp = os.path.join(BASE_DIR, "temp_whatsapp_clipboard.jpg")
        foto.save(ruta_temp)
        success = copiar_imagen_al_portapapeles(ruta_temp)
        return jsonify({"success": success})
    else:
        data = request.json
        ruta_img = data.get('ruta_img')
        if ruta_img:
            ruta_final = os.path.join(BASE_DIR, ruta_img)
            if os.path.exists(ruta_final):
                success = copiar_imagen_al_portapapeles(ruta_final)
                return jsonify({"success": success})
        return jsonify({"success": False, "msg": "Archivo no encontrado"})

@app.route('/guardar_temporal', methods=['POST'])
def guardar_temporal():
    if 'foto' not in request.files: return jsonify({"error": "No hay archivo"}), 400
    foto = request.files['foto']
    ruta_guardado = os.path.join(BASE_DIR, "temp_editada.jpg")
    foto.save(ruta_guardado)
    return jsonify({"success": True, "path": ruta_guardado}), 200

@app.route('/fotos_servidas/<path:filename>')
def serve_fotos(filename):
    return send_from_directory(CARPETA_CAPTURAS, filename)

@app.route('/static/<mes>/<sucursal>/<path:filename>')
def serve_fotos_procesadas(mes, sucursal, filename):
    directorio_foto = os.path.join(BASE_DIR, mes, sucursal)
    return send_from_directory(directorio_foto, filename)

@app.route('/api/subir_foto', methods=['POST'])
def api_subir_foto():
    if 'foto' not in request.files: return "No hay archivo", 400
    foto = request.files['foto']
    filename = request.form.get('filename', foto.filename)
    ruta_guardado = os.path.join(CARPETA_CAPTURAS, filename)
    foto.save(ruta_guardado)
    return "OK", 200

@app.route('/api/guardar_apertura_cierre', methods=['POST'])
def guardar_apertura_cierre():
    data = request.json
    ruta_reportes = os.path.join(BASE_DIR, "reportes_operativos")
    if not os.path.exists(ruta_reportes): os.makedirs(ruta_reportes)
    archivo = os.path.join(ruta_reportes, f"{data['sucursal']}_{data['tipo']}_{datetime.now().strftime('%Y%m%d')}.json")
    with open(archivo, 'w') as f: json.dump(data, f)
    return jsonify({"success": True})

# --- CONFIGURACIONES ---
MESES_ORDENADOS = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
SUCURSALES_GOURMET = ["BOSQUE", "CIRCULO MILITAR", "SAN DIEGO", "GUACARA", "IPSFA", "NAGUANAGUA", "TUCACAS", "SAN RITA", "CASTAÑO"]
SUCURSALES_TODAS = ["ACACIAS", "BARQUISIMETO", "BOSQUE", "CIRCULO MILITAR", "SAN DIEGO", "GUACARA", "IPSFA", "NAGUANAGUA", "TUCACAS", "SAN RITA", "CASTAÑO", "MORA", "SAN JUAN", "VICTORIA", "VILLAS DE ARAGUA"]
INCIDENCIAS_CONFIG = [{"cod": "CNG", "desc": "Colas no gestionadas"}, {"cod": "NZA", "desc": "Neveras ó zonas sin abastecer"}, {"cod": "DPAC", "desc": "Zonas desabastecidas por el personal prev"}, {"cod": "AMSA", "desc": "Apertura de muelle a deshoras sin autorización"}, {"cod": "ODAAAP", "desc": "Obstaculización de tránsito a clientes y acceso a productos"}, {"cod": "CAH", "desc": "Cierres antes de la hora"}, {"cod": "APH", "desc": "Aperturas posterior a la hora"}, {"cod": "ASP", "desc": "Exhibición o área sin personal"}, {"cod": "UIH", "desc": "Uso indebido de herramientas"}, {"cod": "AF", "desc": "Anaquel Frenteado"}, {"cod": "MSP", "desc": "Mantenimiento sin perímetro"}, {"cod": "FFG", "desc": "Falla frigorífica"}, {"cod": "NSI", "desc": "Neveras sin iluminación"}, {"cod": "GSA", "desc": "Gourmet sin abastecer"}]

if not os.path.exists(CARPETA_CAPTURAS): os.makedirs(CARPETA_CAPTURAS)

class CapturaIVMSHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory: return
        filepath = event.src_path
        filename = os.path.basename(filepath)
        ext = os.path.splitext(filename)[1].lower()
        if ext in ['.png', '.jpg', '.jpeg', '.bmp']:
            nombre_upper = filename.upper()
            sucursal_detectada = next((s for s in SUCURSALES_TODAS if s in nombre_upper), "")
            socketio.emit('nueva_captura_ivms', {'filename': filename, 'url_foto': f"/fotos_servidas/{filename}", 'sucursal_sugerida': sucursal_detectada})

def iniciar_watchdog():
    event_handler = CapturaIVMSHandler()
    observer = Observer()
    observer.schedule(event_handler, path=CARPETA_CAPTURAS, recursive=False)
    observer.start()

threading.Thread(target=iniciar_watchdog, daemon=True).start()

def obtener_meses_y_sucursales():
    datos_estructura = {}
    meses_existentes = sorted([d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d)) and d.lower() in MESES_ORDENADOS], key=lambda x: MESES_ORDENADOS.index(x.lower()))
    for mes in meses_existentes:
        ruta_mes = os.path.join(BASE_DIR, mes)
        sucursales = sorted([d for d in os.listdir(ruta_mes) if os.path.isdir(os.path.join(ruta_mes, d))])
        datos_estructura[mes.lower()] = [{"nombre": suc.upper()} for suc in sucursales]
    return meses_existentes, datos_estructura

@app.route('/', methods=['GET', 'POST'])
@app.route('/cargar', methods=['GET', 'POST'])
def cargar_datos():
    if request.method == 'POST':
        fecha = request.form.get('fecha')
        sucursal = request.form.get('sucursal', '').upper()
        incidencia_full = request.form.get('incidencia', 'OP|Operativo') 
        foto = request.files.get('foto')
        edit_report_id = request.form.get('edit_report_id')
        
        # Nuevos campos del formulario
        monitorista = request.form.get('monitorista', '').strip().upper()
        turno = request.form.get('turno', '').strip().upper()
        observaciones = request.form.get('observaciones', '').strip()
        tipo_reporte_real = request.form.get('tipo_reporte_real_post', '').strip()

        if not (fecha and foto):
            return redirect(url_for('cargar_datos'))
            
        if not sucursal:
            sucursal = "GENERAL"
        
        if edit_report_id:
            try:
                hoy_str = datetime.now().strftime("%Y-%m-%d")
                mes_act = MESES_ORDENADOS[datetime.now().month - 1]
                ruta_busqueda_mes = os.path.join(BASE_DIR, mes_act)
                if os.path.exists(ruta_busqueda_mes):
                    for suc_folder in os.listdir(ruta_busqueda_mes):
                        ruta_suc_folder = os.path.join(ruta_busqueda_mes, suc_folder)
                        if os.path.isdir(ruta_suc_folder):
                            for archivo in os.listdir(ruta_suc_folder):
                                if hoy_str in archivo:
                                    partes = archivo.split('_')
                                    if len(partes) >= 3:
                                        ts = partes[2].split('.')[0]
                                        if ts.isdigit() and int(ts) == int(edit_report_id):
                                            os.remove(os.path.join(ruta_suc_folder, archivo))
            except Exception as e:
                print(f"Error eliminando archivo original editado: {e}")

        codigo_incidencia = incidencia_full.split('|')[0]
        
        if request.form.get('tipo_reporte_oculto') == 'apertura_guardia':
            codigo_incidencia = "AG"

        try:
            fecha_dt = datetime.strptime(fecha, "%Y-%m-%d")
            nombre_mes = MESES_ORDENADOS[fecha_dt.month - 1]
        except ValueError:
            return redirect(url_for('cargar_datos'))
            
        carpeta_destino = os.path.join(BASE_DIR, nombre_mes, sucursal)
        if not os.path.exists(carpeta_destino): os.makedirs(carpeta_destino)
        ext = os.path.splitext(secure_filename(foto.filename))[1].lower()
        
        # Encriptamos de forma segura el tipo de reporte real reemplazando espacios por guiones si existe
        tipo_label_limpio = tipo_reporte_real.replace(' ', '-') if tipo_reporte_real else "Incidencia"
        obs_limpia = re.sub(r'[^A-Za-z0-9 ]', '', observaciones).replace(' ', '-')
        
        # Estructura del archivo: CODIGO_FECHA_TIMESTAMP__MONITORISTA__TURNO__OBSERVACIONES__TIPOREPORTE.ext
        nombre_foto_final = f"{codigo_incidencia}_{fecha}_{int(time.time())}__{monitorista}__{turno}__{obs_limpia}__{tipo_label_limpio}{ext}"
        ruta_final = os.path.join(carpeta_destino, nombre_foto_final)
        
        foto.save(ruta_final)
        return redirect(url_for('cargar_datos'))

    return render_template('cargar.html', sucursales=SUCURSALES_TODAS, incidencias=INCIDENCIAS_CONFIG)

@app.route('/panel')
def panel():
    meses_existentes, datos_por_mes = obtener_meses_y_sucursales()
    if not meses_existentes:
        mes_actual = MESES_ORDENADOS[datetime.now().month - 1]
        meses_existentes = [mes_actual]
        datos_por_mes[mes_actual] = []
    ultimo_mes = meses_existentes[-1].lower()
    ranking_data = {}
    for mes in meses_existentes:
        ranking_data[mes.lower()] = {}
        ruta_mes = os.path.join(BASE_DIR, mes)
        if os.path.exists(ruta_mes):
            for suc in os.listdir(ruta_mes):
                ruta_suc = os.path.join(ruta_mes, suc)
                if os.path.isdir(ruta_suc):
                    total_fotos = len([f for f in os.listdir(ruta_suc) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
                    ranking_data[mes.lower()][suc.upper()] = total_fotos
    return render_template('cargar.html', datos_por_mes=datos_por_mes, ultimo_mes=ultimo_mes, datos_ranking_json=json.dumps(ranking_data))

@app.route('/reporte/<mes>/<sucursal>')
def reporte(mes, sucursal):
    mes_target = mes.lower()
    suc_upper = sucursal.upper()
    meses_existentes, _ = obtener_meses_y_sucursales()
    if mes_target not in MESES_ORDENADOS: abort(404)
    idx_limite = MESES_ORDENADOS.index(mes_target) + 1
    meses_historico = [m for m in meses_existentes if MESES_ORDENADOS.index(m.lower()) < idx_limite]
    if mes_target not in meses_historico: meses_historico.append(mes_target)
    v_p = 6.66 if suc_upper in SUCURSALES_GOURMET else 7.14
    datos_filas = []
    totales_meses = [0] * len(meses_historico)
    for inc in INCIDENCIAS_CONFIG:
        if inc['cod'] == "GSA" and suc_upper not in SUCURSALES_GOURMET: continue
        historial_incidencia = []
        for idx_m, m_hist in enumerate(meses_historico):
            ruta_fotos = os.path.join(BASE_DIR, m_hist, suc_upper)
            if os.path.exists(ruta_fotos):
                fotos_validas = [f for f in os.listdir(ruta_fotos) if f.upper().startswith(inc['cod']) and f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                cant = len(fotos_validas)
                fotos_evidencia = []
                for f in fotos_validas:
                    url_foto = url_for('static', filename=f"{m_hist}/{suc_upper}/{f}")
                    fotos_evidencia.append({"url": url_foto})
            else:
                cant = 0
                fotos_evidencia = []
            historial_incidencia.append({"cantidad": cant, "fotos": fotos_evidencia, "mes": m_hist})
            totales_meses[idx_m] += cant
        datos_filas.append({"desc": inc['desc'], "cod": inc['cod'], "history": historial_incidencia})
    return render_template('cargar.html', mes=mes_target, sucursal=suc_upper, meses_historico=meses_historico, datos_filas=datos_filas, totales_meses=totales_meses, v_p=v_p)

@app.route('/control_incidencias')
def control_incidencias():
    incidencias_lista = []
    meses_existentes, _ = obtener_meses_y_sucursales()
    for mes in meses_existentes:
        ruta_mes = os.path.join(BASE_DIR, mes)
        if os.path.exists(ruta_mes):
            for suc in os.listdir(ruta_mes):
                ruta_suc = os.path.join(ruta_mes, suc)
                if os.path.isdir(ruta_suc):
                    for archivo in os.listdir(ruta_suc):
                        if archivo.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                            partes = archivo.split('_')
                            if len(partes) >= 3:
                                codigo = partes[0]
                                fecha = partes[1]
                                timestamp = partes[2].split('__')[0]
                                desc_incidencia = next((i['desc'] for i in INCIDENCIAS_CONFIG if i['cod'] == codigo), codigo)
                                incidencias_lista.append({
                                    "mes": mes,
                                    "sucursal": suc,
                                    "codigo": code,
                                    "descripcion": desc_incidencia,
                                    "fecha": fecha,
                                    "timestamp": int(timestamp) if timestamp.isdigit() else 0,
                                    "archivo": archivo,
                                    "ruta_relativa": f"{mes}/{suc}/{archivo}",
                                    "url_foto": f"/static/{mes}/{suc}/{archivo}"
                                })
    incidencias_lista.sort(key=lambda x: x['timestamp'], reverse=True)
    return render_template('control_incidencias.html', incidencias=incidencias_lista, sucursales=SUCURSALES_TODAS, incidencias_config=INCIDENCIAS_CONFIG)

@app.route('/api/borrar_incidencia', methods=['POST'])
def borrar_incidencia():
    data = request.json
    mes = data.get('mes')
    sucursal = data.get('sucursal')
    archivo = data.get('archivo')
    if mes and sucursal and archivo:
        ruta_archivo = os.path.join(BASE_DIR, mes, sucursal, archivo)
        if os.path.exists(ruta_archivo):
            try:
                os.remove(ruta_archivo)
                return jsonify({"success": True})
            except Exception as e:
                return jsonify({"success": False, "msg": str(e)})
    return jsonify({"success": False, "msg": "Archivo no encontrado"})

@app.route('/api/editar_incidencia', methods=['POST'])
def editar_incidencia():
    data = request.json
    mes_antiguo = data.get('mes_antiguo')
    sucursal_antigua = data.get('sucursal_antigua')
    archivo_antiguo = data.get('archivo_antiguo')
    nueva_fecha = data.get('nueva_fecha')
    nueva_sucursal = data.get('nueva_sucursal').upper()
    nuevo_codigo = data.get('nuevo_codigo')
    
    if not all([mes_antiguo, sucursal_antigua, archivo_antiguo, nueva_fecha, nueva_sucursal, nuevo_codigo]):
        return jsonify({"success": False, "msg": "Faltan datos requeridos"}), 400
        
    ruta_antigua = os.path.join(BASE_DIR, mes_antiguo, sucursal_antigua, archivo_antiguo)
    if not os.path.exists(ruta_antigua):
        return jsonify({"success": False, "msg": "El archivo original no existe"}), 404
        
    try:
        fecha_dt = datetime.strptime(nueva_fecha, "%Y-%m-%d")
        nuevo_mes = MESES_ORDENADOS[fecha_dt.month - 1]
    except ValueError:
        return jsonify({"success": False, "msg": "Formato de fecha inválido"}), 400
        
    ext = os.path.splitext(archivo_antiguo)[1].lower()
    partes = archivo_antiguo.split('_')
    timestamp = partes[2].split('__')[0] if len(partes) >= 3 else int(time.time())
    
    meta_resto = archivo_antiguo.split('__')[1:]
    sufijo_meta = "__" + "__".join(meta_resto) if meta_resto else ext
    
    nuevo_archivo = f"{nuevo_codigo}_{nueva_fecha}_{timestamp}{sufijo_meta}"
    carpeta_destino = os.path.join(BASE_DIR, nuevo_mes, nueva_sucursal)
    
    if not os.path.exists(carpeta_destino):
        os.makedirs(carpeta_destino)
        
    ruta_nueva = os.path.join(carpeta_destino, nuevo_archivo)
    
    try:
        shutil.move(ruta_antigua, ruta_nueva)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)})

@app.route('/api/reportes_del_dia', methods=['GET'])
def reportes_del_dia():
    reportes = []
    hoy = datetime.now().strftime("%Y-%m-%d")
    mes_actual = MESES_ORDENADOS[datetime.now().month - 1]

    ruta_mes = os.path.join(BASE_DIR, mes_actual)
    if os.path.exists(ruta_mes):
        for suc in os.listdir(ruta_mes):
            ruta_suc = os.path.join(ruta_mes, suc)
            if os.path.isdir(ruta_suc):
                for archivo in os.listdir(ruta_suc):
                    if hoy in archivo and archivo.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                        partes = archivo.split('_')
                        if len(partes) >= 3:
                            codigo = partes[0]
                            timestamp = partes[2].split('__')[0]
                            
                            # Desglosamos los metadatos extendidos guardados de forma segura
                            partes_meta = archivo.split('__')
                            monitorista_dec = partes_meta[1] if len(partes_meta) > 1 else ""
                            turno_dec = partes_meta[2] if len(partes_meta) > 2 else ""
                            obs_dec = partes_meta[3].replace('-', ' ') if len(partes_meta) > 3 else "Evidencia registrada en sistema."
                            
                            # Recuperación inteligente del tipo de reporte real
                            tipo_reporte_real = "Incidencia"
                            if len(partes_meta) > 4:
                                tipo_reporte_real = partes_meta[4].split('.')[0].replace('-', ' ')
                            elif codigo == "OP":
                                tipo_reporte_real = "Reporte de Apertura"
                            elif codigo == "AG":
                                tipo_reporte_real = "Apertura de Guardia"

                            desc_incidencia = next((i['desc'] for i in INCIDENCIAS_CONFIG if i['cod'] == codigo), codigo)
                            
                            reportes.append({
                                "id": int(timestamp) if timestamp.isdigit() else int(time.time()),
                                "tipo": tipo_reporte_real, # Enviamos el nombre de reporte real e íntegro
                                "fecha": hoy,
                                "sucursal": suc if suc != "GENERAL" else "",
                                "incidenciaValor": f"{codigo}|{desc_incidencia}",
                                "incidenciaTexto": desc_incidencia,
                                "observaciones": obs_dec,
                                "monitorista": monitorista_dec,
                                "turno": turno_dec,
                                "nombreFoto": archivo,
                                "ruta_relativa": f"{mes_actual}/{suc}/{archivo}"
                            })
                            
    reportes.sort(key=lambda x: x['id'], reverse=True)
    return jsonify(reportes)

@app.route('/api/reportes/<int:report_id>', methods=['DELETE'])
def eliminar_reporte_dia(report_id):
    hoy = datetime.now().strftime("%Y-%m-%d")
    mes_actual = MESES_ORDENADOS[datetime.now().month - 1]
    
    ruta_mes = os.path.join(BASE_DIR, mes_actual)
    if os.path.exists(ruta_mes):
        for suc in os.listdir(ruta_mes):
            ruta_suc = os.path.join(ruta_mes, suc)
            if os.path.isdir(ruta_suc):
                for archivo in os.listdir(ruta_suc):
                    if hoy in archivo:
                        partes = archivo.split('_')
                        if len(partes) >= 3:
                            timestamp = partes[2].split('__')[0]
                            if timestamp.isdigit() and int(timestamp) == report_id:
                                try:
                                    os.remove(os.path.join(ruta_suc, archivo))
                                    return jsonify({"success": True})
                                except Exception as e:
                                    return jsonify({"success": False, "msg": str(e)})

    return jsonify({"success": False, "msg": "Reporte no encontrado o ya eliminado."}), 404

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5006)