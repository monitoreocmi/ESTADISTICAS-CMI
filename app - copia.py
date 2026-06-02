import os
import math
import json
import threading
import time
import shutil
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

# Configuración Híbrida de Carpetas
app = Flask(__name__, static_folder='.', static_url_path='', template_folder='.')
app.secret_key = 'luxor_fiscalizacion_fiscalizacion_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

# --- RUTA DEFINITIVA PARA LAS FOTOS ---
CARPETA_CAPTURAS = r"C:\Users\Admin\Desktop\FISCALIZACION\fotos_incidencias"

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

@app.route('/api/preparar_whatsapp', methods=['POST'])
def preparar_whatsapp():
    data = request.json
    nombre_archivo = data.get('ruta_img')
    
    # 1. Intentar buscar en la carpeta del script (temporales)
    ruta_local = os.path.join(os.path.dirname(os.path.abspath(__file__)), nombre_archivo)
    # 2. Intentar buscar en la carpeta de capturas definida
    ruta_capturas = os.path.join(CARPETA_CAPTURAS, nombre_archivo)
    
    ruta_final = ruta_local if os.path.exists(ruta_local) else (ruta_capturas if os.path.exists(ruta_capturas) else None)
        
    if ruta_final:
        success = copiar_imagen_al_portapapeles(ruta_final)
        return jsonify({"success": success})
    
    return jsonify({"success": False, "msg": "Archivo no encontrado"})

@app.route('/guardar_temporal', methods=['POST'])
def guardar_temporal():
    if 'foto' not in request.files:
        return jsonify({"success": False}), 400
    foto = request.files['foto']
    ruta_guardado = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_evidencia.jpg")
    foto.save(ruta_guardado)
    return jsonify({"success": True})

@app.route('/fotos_servidas/<path:filename>')
def serve_fotos(filename):
    return send_from_directory(CARPETA_CAPTURAS, filename)

@app.route('/static/<mes>/<sucursal>/<path:filename>')
def serve_fotos_procesadas(mes, sucursal, filename):
    ruta_raiz = os.path.dirname(os.path.abspath(__file__))
    directorio_foto = os.path.join(ruta_raiz, mes, sucursal)
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
    ruta_reportes = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reportes_operativos")
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
            socketio.emit('nueva_captura_ivms', {
                'filename': filename,
                'url_foto': f"/fotos_servidas/{filename}",
                'sucursal_sugerida': sucursal_detectada
            })

def iniciar_watchdog():
    event_handler = CapturaIVMSHandler()
    observer = Observer()
    observer.schedule(event_handler, path=CARPETA_CAPTURAS, recursive=False)
    observer.start()

threading.Thread(target=iniciar_watchdog, daemon=True).start()

def obtener_meses_y_sucursales():
    ruta_raiz = os.path.dirname(os.path.abspath(__file__))
    datos_estructura = {}
    meses_existentes = sorted([d for d in os.listdir(ruta_raiz) if os.path.isdir(os.path.join(ruta_raiz, d)) and d.lower() in MESES_ORDENADOS], key=lambda x: MESES_ORDENADOS.index(x.lower()))
    for mes in meses_existentes:
        ruta_mes = os.path.join(ruta_raiz, mes)
        sucursales = sorted([d for d in os.listdir(ruta_mes) if os.path.isdir(os.path.join(ruta_raiz, mes, d))])
        datos_estructura[mes.lower()] = [{"nombre": suc.upper()} for suc in sucursales]
    return meses_existentes, datos_estructura

@app.route('/')
@app.route('/cargar', methods=['GET', 'POST'])
def cargar_datos():
    if request.method == 'POST':
        fecha = request.form.get('fecha')
        sucursal = request.form.get('sucursal', '').upper()
        incidencia = request.form.get('incidencia', '')
        foto = request.files.get('foto')
        if not (fecha and sucursal and incidencia and foto):
            flash("❌ Todos los campos son obligatorios", "error")
            return redirect(url_for('cargar_datos'))
        try:
            fecha_dt = datetime.strptime(fecha, "%Y-%m-%d")
            nombre_mes = MESES_ORDENADOS[fecha_dt.month - 1]
        except ValueError:
            flash("❌ Formato de fecha inválido", "error")
            return redirect(url_for('cargar_datos'))
        ruta_raiz = os.path.dirname(os.path.abspath(__file__))
        carpeta_destino = os.path.join(ruta_raiz, nombre_mes, sucursal)
        if not os.path.exists(carpeta_destino): os.makedirs(carpeta_destino)
        ext = os.path.splitext(secure_filename(foto.filename))[1].lower()
        if ext not in ['.png', '.jpg', '.jpeg']:
            flash("❌ Formato de imagen no permitido", "error")
            return redirect(url_for('cargar_datos'))
        nombre_foto_final = f"{incidencia}_{fecha}_{int(time.time())}{ext}"
        ruta_final = os.path.join(carpeta_destino, nombre_foto_final)
        foto.save(ruta_final)
        flash(f"✨ Incidencia [{incidencia}] guardada.", "success")
        return redirect(url_for('cargar_datos'))
    return render_template('templates/cargar.html', sucursales=SUCURSALES_TODAS, incidencias=INCIDENCIAS_CONFIG)

@app.route('/panel')
def panel():
    meses_existentes, datos_por_mes = obtener_meses_y_sucursales()
    if not meses_existentes:
        mes_actual = MESES_ORDENADOS[datetime.now().month - 1]
        meses_existentes = [mes_actual]
        datos_por_mes[mes_actual] = []
    ultimo_mes = meses_existentes[-1].lower()
    ranking_data = {}
    ruta_raiz = os.path.dirname(os.path.abspath(__file__))
    for mes in meses_existentes:
        ranking_data[mes.lower()] = {}
        ruta_mes = os.path.join(ruta_raiz, mes)
        if os.path.exists(ruta_mes):
            for suc in os.listdir(ruta_mes):
                ruta_suc = os.path.join(ruta_mes, suc)
                if os.path.isdir(ruta_suc):
                    total_fotos = len([f for f in os.listdir(ruta_suc) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
                    ranking_data[mes.lower()][suc.upper()] = total_fotos
    return render_template('panel.html', datos_por_mes=datos_por_mes, ultimo_mes=ultimo_mes, datos_ranking_json=json.dumps(ranking_data))

@app.route('/reporte/<mes>/<sucursal>')
def reporte(mes, sucursal):
    mes_target = mes.lower()
    suc_upper = sucursal.upper()
    ruta_raiz = os.path.dirname(os.path.abspath(__file__))
    meses_existentes, _ = obtener_meses_y_sucursales()
    if mes_target not in MESES_ORDENADOS: abort(404, description="Mes no configurado")
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
            ruta_fotos = os.path.join(ruta_raiz, m_hist, suc_upper)
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
    suma_azul = 0
    for fila in datos_filas:
        valores_numericos = [h['cantidad'] for h in fila['history']]
        if valores_numericos:
            cant_actual = valores_numericos[-1]
            if len(valores_numericos) == 1 or cant_actual <= min(valores_numericos[:-1]): suma_azul += v_p
    if totales_meses and (len(totales_meses) == 1 or totales_meses[-1] <= min(totales_meses[:-1])): suma_azul += v_p
    return render_template('reporte.html', mes=mes_target, sucursal=suc_upper, meses_historico=meses_historico, datos_filas=datos_filas, totales_meses=totales_meses, v_p=v_p, suma_azul=suma_azul)

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5006)