import os
import sys
import math
import shutil
import json
from datetime import datetime

# --- DATOS OFICIALES C.M.I. FEBRERO 2026 ---
DATOS_FEBRERO_OFICIAL = {
    "ACACIAS": {"CNG": 6, "NZA": 40, "DPAC": 0, "AMSA": 0, "ODAAAP": 2, "CAH": 0, "APH": 0, "ASP": 0, "UIH": 0, "AF": 2, "MSP": 0, "FFG": 0, "NSI": 0, "TOTAL": 50},
    "BARQUISIMETO": {"CNG": 0, "NZA": 20, "DPAC": 0, "AMSA": 0, "ODAAAP": 2, "CAH": 0, "APH": 0, "ASP": 0, "UIH": 0, "AF": 1, "MSP": 0, "FFG": 0, "NSI": 0, "TOTAL": 23},
    "BOSQUE": {"CNG": 16, "NZA": 18, "GSA": 7, "DPAC": 0, "AMSA": 0, "ODAAAP": 4, "CAH": 0, "APH": 0, "ASP": 0, "UIH": 0, "AF": 1, "MSP": 0, "FFG": 0, "NSI": 0, "TOTAL": 46},
    "CIRCULO MILITAR": {"CNG": 3, "NZA": 40, "GSA": 1, "DPAC": 1, "AMSA": 0, "ODAAAP": 5, "CAH": 0, "APH": 2, "ASP": 0, "UIH": 0, "AF": 0, "MSP": 0, "FFG": 0, "NSI": 0, "TOTAL": 52},
    "EUROMAXX VILLAS DE ARAGUA": {"CNG": 0, "NZA": 34, "DPAC": 0, "AMSA": 0, "ODAAAP": 1, "CAH": 0, "APH": 0, "ASP": 0, "UIH": 0, "AF": 0, "MSP": 0, "FFG": 0, "NSI": 1, "TOTAL": 36},
    "EUROMAXX SAN DIEGO": {"CNG": 2, "NZA": 79, "GSA": 0, "DPAC": 13, "AMSA": 0, "ODAAAP": 2, "CAH": 0, "APH": 0, "ASP": 0, "UIH": 0, "AF": 3, "MSP": 0, "FFG": 0, "NSI": 0, "TOTAL": 99},
    "GUACARA": {"CNG": 0, "NZA": 49, "GSA": 1, "DPAC": 0, "AMSA": 0, "ODAAAP": 6, "CAH": 0, "APH": 0, "ASP": 0, "UIH": 0, "AF": 3, "MSP": 0, "FFG": 0, "NSI": 0, "TOTAL": 59},
    "IPSFA": {"CNG": 0, "NZA": 45, "GSA": 9, "DPAC": 1, "AMSA": 0, "ODAAAP": 5, "CAH": 0, "APH": 0, "ASP": 0, "UIH": 0, "AF": 1, "MSP": 1, "FFG": 0, "NSI": 0, "TOTAL": 62},
    "MORA": {"CNG": 1, "NZA": 19, "DPAC": 0, "AMSA": 0, "ODAAAP": 2, "CAH": 0, "APH": 0, "ASP": 0, "UIH": 0, "AF": 0, "MSP": 0, "FFG": 0, "NSI": 0, "TOTAL": 22},
    "NAGUANAGUA": {"CNG": 7, "NZA": 45, "GSA": 0, "DPAC": 0, "AMSA": 0, "ODAAAP": 1, "CAH": 0, "APH": 0, "ASP": 0, "UIH": 0, "AF": 0, "MSP": 0, "FFG": 1, "NSI": 1, "TOTAL": 55},
    "TUCACAS": {"CNG": 2, "NZA": 4, "GSA": 0, "DPAC": 0, "AMSA": 0, "ODAAAP": 7, "CAH": 0, "APH": 0, "ASP": 0, "UIH": 0, "AF": 0, "MSP": 0, "FFG": 0, "NSI": 0, "TOTAL": 13},
    "SAN JUAN": {"CNG": 8, "NZA": 59, "DPAC": 0, "AMSA": 0, "ODAAAP": 2, "CAH": 0, "APH": 0, "ASP": 0, "UIH": 0, "AF": 0, "MSP": 1, "FFG": 0, "NSI": 3, "TOTAL": 73},
    "SANTA RITA": {"CNG": 4, "NZA": 35, "GSA": 0, "DPAC": 2, "AMSA": 0, "ODAAAP": 1, "CAH": 0, "APH": 0, "ASP": 0, "UIH": 0, "AF": 0, "MSP": 0, "FFG": 0, "NSI": 0, "TOTAL": 42},
    "VICTORIA": {"CNG": 3, "NZA": 65, "DPAC": 0, "AMSA": 0, "ODAAAP": 9, "CAH": 0, "APH": 0, "ASP": 0, "UIH": 0, "AF": 1, "MSP": 0, "FFG": 0, "NSI": 0, "TOTAL": 78},
    "CASTAÑO": {"CNG": 0, "NZA": 9, "GSA": 0, "DPAC": 0, "AMSA": 0, "ODAAAP": 1, "CAH": 0, "APH": 0, "ASP": 0, "UIH": 0, "AF": 0, "MSP": 0, "FFG": 0, "NSI": 0, "TOTAL": 10}
}

incidencias_config = [
    {"cod": "CNG", "desc": "Colas no gestionadas"}, {"cod": "NZA", "desc": "Neveras ó zonas sin abastecer"},
    {"cod": "DPAC", "desc": "Zonas desabastecidas por el personal prev"}, {"cod": "AMSA", "desc": "Apertura de muelle a deshoras sin autorización"},
    {"cod": "ODAAAP", "desc": "Obstaculización de tránsito a clientes y acceso a productos"}, {"cod": "CAH", "desc": "Cierres antes de la hora"},
    {"cod": "APH", "desc": "Aperturas posterior a la hora"}, {"cod": "ASP", "desc": "Exhibición o área sin personal"},
    {"cod": "UIH", "desc": "Uso indebido de herramientas"}, {"cod": "AF", "desc": "Anaquel Frenteado"},
    {"cod": "MSP", "desc": "Mantenimiento sin perímetro"}, {"cod": "FFG", "desc": "Falla frigorífica"},
    {"cod": "NSI", "desc": "Neveras sin iluminación"}, {"cod": "GSA", "desc": "Gourmet sin abastecer"}
]

SUCURSALES_GOURMET = ["BOSQUE", "CIRCULO MILITAR", "SAN DIEGO", "GUACARA", "IPSFA", "NAGUANAGUA", "TUCACAS", "SAN RITA", "CASTAÑO"]
MESES_ORDENADOS = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']

CSS_BASE = """
<style>
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css');
    body { font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; background-color: #0047AB; color: #1A1D4D; }
    .logo { width: 120px; height: auto; position: absolute; top: 15px; left: 15px; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3)); }
    .report-container { max-width: 1200px; margin: 50px auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); border-bottom: 8px solid #F9D908; }
    .report-title { text-align: center; font-size: 28px; color: #1A1D4D; margin-bottom: 30px; text-transform: uppercase; font-weight: 800; }
    table { width: 100%; border-collapse: collapse; margin-bottom: 20px; background: white; table-layout: auto; }
    th { background-color: #1A1D4D; color: white; padding: 12px; text-transform: uppercase; font-size: 0.85rem; white-space: nowrap; }
    td { border: 1px solid #ddd; padding: 10px; text-align: center; font-weight: bold; font-size: 0.9rem; }
    .col-incidencia { text-align: left; width: 30%; min-width: 200px; }
    .fila-total { color: #1A1D4D !important; font-size: 1.1rem; border-top: 2px solid #1A1D4D; }
    .rojo { background-color: #E61E25 !important; color: white !important; }
    .azul { background-color: #00B0F0 !important; color: white !important; }
    .score-final { font-size: 3.5rem !important; vertical-align: middle; font-weight: 900; }
    .botones-footer { display: flex; justify-content: center; gap: 20px; margin-top: 30px; }
    .btn-volver { background-color: #1A1D4D; color: white; padding: 12px 25px; border-radius: 8px; text-decoration: none; display: inline-flex; align-items: center; gap: 10px; font-weight: bold; border: 2px solid #F9D908; cursor: pointer; }
    .btn-volver:hover { background-color: #F9D908; color: #1A1D4D; }
    .gallery-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 20px; margin-top: 20px; }
    .gallery-card { background: #f4f4f4; border-radius: 10px; overflow: hidden; border: 2px solid #ddd; text-align: center; }
    .img-container { height: 180px; width: 100%; cursor: pointer; }
    .img-container img { width: 100%; height: 100%; object-fit: cover; }
    .date-label { padding: 8px; font-size: 0.85rem; color: #555; font-weight: bold; background: #fff; border-top: 1px solid #eee; }
    .modal { display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.9); justify-content: center; align-items: center; }
    .modal-content { max-width: 90%; max-height: 90%; border: 5px solid white; border-radius: 10px; }
    .close-modal { position: absolute; top: 20px; right: 35px; color: #fff; font-size: 40px; font-weight: bold; cursor: pointer; }
</style>
"""

JS_MODAL = "<script>function openModal(imgSrc){const m=document.getElementById('myModal');const i=document.getElementById('img01');m.style.display='flex';i.src=imgSrc;} function closeModal(){document.getElementById('myModal').style.display='none';} window.onclick=function(e){if(e.target==document.getElementById('myModal'))closeModal();}</script>"

def obtener_semana_del_archivo(ruta_archivo):
    """Determina la semana (semana1 a semana5) según el día de modificación de la foto."""
    try:
        t_mod = os.path.getmtime(ruta_archivo)
        dia = datetime.fromtimestamp(t_mod).day
        if dia <= 7: return "semana1"
        elif dia <= 14: return "semana2"
        elif dia <= 21: return "semana3"
        elif dia <= 28: return "semana4"
        else: return "semana5"
    except:
        return "semana1"

def ejecutar_reportes():
    try:
        ruta_base = os.path.dirname(os.path.abspath(sys.argv[0]))
        os.chdir(ruta_base)
        print("\n" + "="*60 + "\n🚀 GENERADOR LUXOR - EVALUACIONES SEMANALES HISTÓRICAS\n" + "="*60)

        id_ranking_datos = {}

        # Limpieza 6 meses
        fecha_hoy = datetime.now()
        conservar = [MESES_ORDENADOS[(fecha_hoy.month - 1 - i) % 12] for i in range(6)]
        for item in os.listdir('.'):
            if os.path.isdir(item) and item.lower() in MESES_ORDENADOS and item.lower() not in conservar:
                print(f"   🗑️ Eliminando antiguo: {item.upper()}"); shutil.rmtree(item)

        meses_existentes = sorted([d for d in os.listdir('.') if os.path.isdir(d) and d.lower() in MESES_ORDENADOS], key=lambda x: MESES_ORDENADOS.index(x.lower()))

        for idx_m, mes_n in enumerate(meses_existentes):
            print(f"\n📂 PROCESANDO MES: {mes_n.upper()}")
            
            id_ranking_datos[mes_n.lower()] = {
                "mensual": {},
                "semanas": {f"semana{i}": {} for i in range(1, 6)}
            }
            
            ruta_mes = os.path.join(ruta_base, mes_n)
            sucursales = [d for d in os.listdir(ruta_mes) if os.path.isdir(os.path.join(ruta_mes, d))]

            for suc in sucursales:
                print(f"   |-- Sucursal: {suc}")
                ruta_suc = os.path.join(ruta_mes, suc)
                suc_upper = suc.upper()
                v_p = 6.66 if suc_upper in SUCURSALES_GOURMET else 7.14
                
                filas_html, totales_meses, datos_filas = "", [0]*(idx_m+1), []

                semanas_keys = ["semana1", "semana2", "semana3", "semana4", "semana5"]
                
                # Diccionario para agrupar las fotos clasificadas por semana real
                fotos_por_semana_incidencia = {sem: {inc['cod']: [] for inc in incidencias_config} for sem in semanas_keys}
                conteo_semanal_sucursal = {sem: {inc['cod']: 0 for inc in incidencias_config} for sem in semanas_keys}
                totales_semanales_sucursal = {sem: 0 for sem in semanas_keys}

                for inc in incidencias_config:
                    if inc['cod'] == "GSA" and suc_upper not in SUCURSALES_GOURMET: continue
                    hist = []
                    for i_m in range(idx_m + 1):
                        m_nombre = meses_existentes[i_m]
                        if m_nombre.lower() == "febrero" and suc_upper in DATOS_FEBRERO_OFICIAL:
                            c = DATOS_FEBRERO_OFICIAL[suc_upper].get(inc['cod'], 0)
                            if i_m == idx_m:
                                conteo_semanal_sucursal["semana1"][inc['cod']] = c
                                totales_semanales_sucursal["semana1"] += c
                        else:
                            p_fotos = os.path.join(ruta_base, m_nombre, suc)
                            fotos_encontradas = [f for f in os.listdir(p_fotos) if f.upper().startswith(inc['cod']) and f.lower().endswith(('.png','.jpg','.jpeg'))] if os.path.exists(p_fotos) else []
                            c = len(fotos_encontradas)
                            
                            if i_m == idx_m and os.path.exists(p_fotos):
                                for f in fotos_encontradas:
                                    sem_pert = obtener_semana_del_archivo(os.path.join(p_fotos, f))
                                    conteo_semanal_sucursal[sem_pert][inc['cod']] += 1
                                    totales_semanales_sucursal[sem_pert] += 1
                                    fotos_por_semana_incidencia[sem_pert][inc['cod']].append(f)
                                    
                        hist.append(c); totales_meses[i_m] += c
                    datos_filas.append({"desc": inc['desc'], "cod": inc['cod'], "hist": hist})

                id_ranking_datos[mes_n.lower()]["mensual"][suc_upper] = totales_meses[idx_m]

                # --- PROCESO Y CÁLCULO MENSUAL ---
                suma_azul = sum(v_p for it in datos_filas if idx_m == 0 or it['hist'][idx_m] <= min(it['hist'][:idx_m])) + (v_p if idx_m == 0 or totales_meses[idx_m] <= min(totales_meses[:idx_m]) else 0)
                res_final = min(100, math.ceil(suma_azul / 5) * 5)
                clase_f = "azul" if res_final >= 70 else "rojo"

                for idx_f, item in enumerate(datos_filas):
                    tr = f"<td class='col-incidencia'>{item['desc']}</td>"
                    for i, cant in enumerate(item['hist']):
                        clase = "azul" if (i > 0 and cant <= min(item['hist'][:i])) else ("" if i==0 else "rojo")
                        ruta_f_fotos = os.path.join(ruta_base, meses_existentes[i], suc)
                        fotos = [f for f in os.listdir(ruta_f_fotos) if f.upper().startswith(item['cod']) and f.lower().endswith(('.png','.jpg','.jpeg'))] if os.path.exists(ruta_f_fotos) else []
                        
                        if cant > 0 and fotos:
                            n_gal = f"GAL_{item['cod']}_{suc_upper}_DE_{meses_existentes[i].upper()}_PARA_{mes_n.upper()}.html"
                            btn_back = f"REPORTE_{suc_upper}_{mes_n.upper()}.html" if i == idx_m else f"../../{mes_n}/{suc}/REPORTE_{suc_upper}_{mes_n.upper()}.html"
                            cards_html = "".join([f"<div class='gallery-card'><div class='img-container' onclick='openModal(\"{f}\")'><img src='{f}'></div><div class='date-label'>{os.path.splitext(f.replace(item['cod'],'').strip())[0]}</div></div>" for f in fotos])
                            
                            with open(os.path.join(ruta_f_fotos, n_gal), "w", encoding="utf-8") as fg:
                                fg.write(f"<html><head><meta charset='UTF-8'>{CSS_BASE}</head><body><div class='report-container'><h1 class='report-title'>{item['desc']} ({meses_existentes[i].upper()})</h1><div class='gallery-grid'>{cards_html}</div><div class='botones-footer'><a href='{btn_back}' class='btn-volver'><i class='fas fa-arrow-left'></i> Volver</a></div></div><div id='myModal' class='modal'><span class='close-modal' onclick='closeModal()'>&times;</span><img class='modal-content' id='img01'></div>{JS_MODAL}</body></html>")
                            
                            link = f"../../{meses_existentes[i]}/{suc}/{n_gal}" if i != idx_m else n_gal
                            tr += f"<td class='{clase}'><a href='{link}' style='color:inherit;text-decoration:none'>{cant}</a></td>"
                        else: tr += f"<td class='{clase}'>{cant}</td>"
                    
                    tr += f"<td>{v_p}%</td>"
                    if idx_f == 0: tr += f"<td rowspan='{len(datos_filas)+1}' class='{clase_f} score-final'>{res_final}%</td>"
                    filas_html += f"<tr>{tr}</tr>"

                f_total = f"<tr class='fila-total'><td>TOTAL</td>" + "".join([f"<td class='{'azul' if (i>0 and t<=min(totales_meses[:i])) else ('' if i==0 else 'rojo')}'>{t}</td>" for i, t in enumerate(totales_meses)]) + f"<td>{v_p}%</td></tr>"
                
                with open(os.path.join(ruta_suc, f"REPORTE_{suc_upper}_{mes_n.upper()}.html"), "w", encoding="utf-8") as fr:
                    fr.write(f"""<html><head><meta charset='UTF-8'>{CSS_BASE}</head><body><img src='../../RECURSOS/logo.png' class='logo'><div class='report-container'><h1 class='report-title'>DATOS CLAVES - {suc} ({mes_n.upper()})</h1><table><thead><tr><th>Incidencia</th>{"".join([f"<th>{m.upper()}</th>" for m in meses_existentes[:idx_m+1]])}<th></th><th></th></tr></thead><tbody>{filas_html}{f_total}</tbody></table><div class='botones-footer'><a href='../../panel.html' class='btn-volver'><i class='fas fa-home'></i> Menú Principal</a></div></div></body></html>""")


                # --- NUEVA GENERACIÓN DE REPORTES SEMANALES CON HISTÓRICO ACUMULATIVO ---
                for idx_s, sem_key in enumerate(semanas_keys):
                    semanas_visibles = semanas_keys[:idx_s+1] # Trae semanas acumuladas (ej: s1, s2 y s3)
                    
                    # Calcular nota real de la semana evaluada
                    conteo_incidencias_actual = conteo_semanal_sucursal[sem_key]
                    total_semana_actual = totales_semanales_sucursal[sem_key]
                    suma_azul_sem = sum(v_p for inc_c, cant in conteo_incidencias_actual.items() if not (inc_c == "GSA" and suc_upper not in SUCURSALES_GOURMET) and cant == 0)
                    res_final_sem = min(100, math.ceil(suma_azul_sem / 5) * 5)
                    if total_semana_actual > 0 and res_final_sem == 100: res_final_sem = 95
                    if total_semana_actual == 0: res_final_sem = 100
                    
                    id_ranking_datos[mes_n.lower()]["semanas"][sem_key][suc_upper] = res_final_sem
                    clase_f_sem = "azul" if res_final_sem >= 70 else "rojo"
                    
                    filas_html_sem = ""
                    for idx_inc, inc in enumerate(incidencias_config):
                        if inc['cod'] == "GSA" and suc_upper not in SUCURSALES_GOURMET: continue
                        
                        tr_sem = f"<td class='col-incidencia'>{inc['desc']}</td>"
                        valores_historicos_semanas = [conteo_semanal_sucursal[s].get(inc['cod'], 0) for s in semanas_visibles]
                        
                        for i_s, cant_sem in enumerate(valores_historicos_semanas):
                            # Regla Luxor: Azul si es menor o igual al histórico previo de semanas
                            clase_c_sem = "azul" if (i_s > 0 and cant_sem <= min(valores_historicos_semanas[:i_s])) else ("" if i_s == 0 else "rojo")
                            sem_nombre_iterada = semanas_visibles[i_s]
                            fotos_sem = fotos_por_semana_incidencia[sem_nombre_iterada].get(inc['cod'], [])
                            
                            if cant_sem > 0 and fotos_sem:
                                n_gal_sem = f"GAL_SEMANAL_{inc['cod']}_{suc_upper}_{sem_nombre_iterada.upper()}_PARA_{mes_n.upper()}.html"
                                cards_html_sem = "".join([f"<div class='gallery-card'><div class='img-container' onclick='openModal(\"{f}\")'><img src='{f}'></div><div class='date-label'>{f}</div></div>" for f in fotos_sem])
                                
                                with open(os.path.join(ruta_suc, n_gal_sem), "w", encoding="utf-8") as fg_sem:
                                    fg_sem.write(f"<html><head><meta charset='UTF-8'>{CSS_BASE}</head><body><div class='report-container'><h1 class='report-title'>{inc['desc']} ({sem_nombre_iterada.upper()})</h1><div class='gallery-grid'>{cards_html_sem}</div><div class='botones-footer'><a href='REPORTE_{suc_upper}_{mes_n.upper()}_{sem_key.upper()}.html' class='btn-volver'><i class='fas fa-arrow-left'></i> Volver</a></div></div><div id='myModal' class='modal'><span class='close-modal' onclick='closeModal()'>&times;</span><img class='modal-content' id='img01'></div>{JS_MODAL}</body></html>")
                                
                                tr_sem += f"<td class='{clase_c_sem}'><a href='{n_gal_sem}' style='color:inherit;text-decoration:none'>{cant_sem}</a></td>"
                            else:
                                tr_sem += f"<td class='{clase_c_sem}'>{cant_sem}</td>"
                                
                        tr_sem += f"<td>{v_p}%</td>"
                        if idx_inc == 0:
                            tr_sem += f"<td rowspan='{len(conteo_incidencias_actual)+1}' class='{clase_f_sem} score-final'>{res_final_sem}%</td>"
                        filas_html_sem += f"<tr>{tr_sem}</tr>"
                        
                    # Fila de Totales por Semana
                    totales_historicos_semanas = [totales_semanales_sucursal[s] for s in semanas_visibles]
                    f_total_sem = f"<tr class='fila-total'><td>TOTAL</td>"
                    for i_s, t_sem in enumerate(totales_historicos_semanas):
                        clase_tot_sem = "azul" if (i_s > 0 and t_sem <= min(totales_historicos_semanas[:i_s])) else ("" if i_s == 0 else "rojo")
                        f_total_sem += f"<td class='{clase_tot_sem}'>{t_sem}</td>"
                    f_total_sem += f"<td>{v_p}%</td></tr>"
                    
                    header_semanas = "".join([f"<th>SEMANA {s[-1]}</th>" for s in semanas_visibles])
                    nombre_html_semana = f"REPORTE_{suc_upper}_{mes_n.upper()}_{sem_key.upper()}.html"
                    
                    with open(os.path.join(ruta_suc, nombre_html_semana), "w", encoding="utf-8") as fs:
                        fs.write(f"""<html><head><meta charset='UTF-8'>{CSS_BASE}</head><body><img src='../../RECURSOS/logo.png' class='logo'><div class='report-container'><h1 class='report-title'>DATOS CLAVES {sem_key.upper()} - {suc_upper} ({mes_n.upper()})</h1><table><thead><tr><th>Incidencia</th>{header_semanas}<th>VALOR P.</th><th>PUNTAJE</th></tr></thead><tbody>{filas_html_sem}{f_total_sem}</tbody></table><div class='botones-footer'><a href='../../panel.html' class='btn-volver'><i class='fas fa-home'></i> Menú Principal</a></div></div></body></html>""")

        with open("datos_ranking.json", "w", encoding="utf-8") as jf:
            json.dump(id_ranking_datos, jf, indent=4)

        print("\n" + "="*60 + "\n✅ REPORTES MENSUALES, ACUMULATIVOS SEMANALES Y GALERÍAS COMPLETADOS\n" + "="*60)
    except Exception as e: 
        print(f"\n❌ ERROR: {e}")
    input("\nPresiona Enter para cerrar...")

if __name__ == "__main__": ejecutar_reportes()