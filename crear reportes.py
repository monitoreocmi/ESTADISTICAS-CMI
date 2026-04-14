import os
import sys
import math
import shutil
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

def ejecutar_reportes():
    try:
        ruta_base = os.path.dirname(os.path.abspath(sys.argv[0]))
        os.chdir(ruta_base)
        print("\n" + "="*60 + "\n🚀 GENERADOR LUXOR - DEPURACIÓN ACTIVADA\n" + "="*60)

        # 1. Limpieza 6 meses
        fecha_hoy = datetime.now()
        conservar = [MESES_ORDENADOS[(fecha_hoy.month - 1 - i) % 12] for i in range(6)]
        for item in os.listdir('.'):
            if os.path.isdir(item) and item.lower() in MESES_ORDENADOS and item.lower() not in conservar:
                print(f"   🗑️ Eliminando antiguo: {item.upper()}"); shutil.rmtree(item)

        meses_existentes = sorted([d for d in os.listdir('.') if os.path.isdir(d) and d.lower() in MESES_ORDENADOS], key=lambda x: MESES_ORDENADOS.index(x.lower()))

        for idx_m, mes_n in enumerate(meses_existentes):
            print(f"\n📂 PROCESANDO MES: {mes_n.upper()}")
            ruta_mes = os.path.join(ruta_base, mes_n)
            sucursales = [d for d in os.listdir(ruta_mes) if os.path.isdir(os.path.join(ruta_mes, d))]

            for suc in sucursales:
                print(f"   |-- Sucursal: {suc}")
                # DEFINICIÓN EXPLÍCITA DE RUTA_SUC
                ruta_suc = os.path.join(ruta_mes, suc)
                suc_upper = suc.upper()
                v_p = 6.66 if suc_upper in SUCURSALES_GOURMET else 7.14
                
                filas_html, totales_meses, datos_filas = "", [0]*(idx_m+1), []

                for inc in incidencias_config:
                    if inc['cod'] == "GSA" and suc_upper not in SUCURSALES_GOURMET: continue
                    hist = []
                    for i_m in range(idx_m + 1):
                        m_nombre = meses_existentes[i_m]
                        if m_nombre.lower() == "febrero" and suc_upper in DATOS_FEBRERO_OFICIAL:
                            c = DATOS_FEBRERO_OFICIAL[suc_upper].get(inc['cod'], 0)
                        else:
                            p_fotos = os.path.join(ruta_base, m_nombre, suc)
                            c = len([f for f in os.listdir(p_fotos) if f.upper().startswith(inc['cod']) and f.lower().endswith(('.png','.jpg','.jpeg'))]) if os.path.exists(p_fotos) else 0
                        hist.append(c); totales_meses[i_m] += c
                    datos_filas.append({"desc": inc['desc'], "cod": inc['cod'], "hist": hist})

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
                            btn_back = f"REPORTE_{suc_upper}_{mes_n.upper()}.html"
                            if i != idx_m:
                                btn_back = f"../../{mes_n}/{suc}/REPORTE_{suc_upper}_{mes_n.upper()}.html"

                            cards_html = "".join([f"<div class='gallery-card'><div class='img-container' onclick='openModal(\"{f}\")'><img src='{f}'></div><div class='date-label'>{os.path.splitext(f.replace(item['cod'],'').strip())[0]}</div></div>" for f in fotos])
                            
                            with open(os.path.join(ruta_f_fotos, n_gal), "w", encoding="utf-8") as fg:
                                fg.write(f"<html><head><meta charset='UTF-8'>{CSS_BASE}</head><body><div class='report-container'><h1 class='report-title'>{item['desc']} ({meses_existentes[i].upper()})</h1><div class='gallery-grid'>{cards_html}</div><div class='botones-footer'><a href='{btn_back}' class='btn-volver'><i class='fas fa-arrow-left'></i> Volver al Reporte {mes_n.upper()}</a><a href='../../panel.html' class='btn-volver'><i class='fas fa-home'></i> Menú Principal</a></div></div><div id='myModal' class='modal'><span class='close-modal' onclick='closeModal()'>&times;</span><img class='modal-content' id='img01'></div>{JS_MODAL}</body></html>")
                            
                            link = f"../../{meses_existentes[i]}/{suc}/{n_gal}" if i != idx_m else n_gal
                            tr += f"<td class='{clase}'><a href='{link}' style='color:inherit;text-decoration:none'>{cant}</a></td>"
                        else: tr += f"<td class='{clase}'>{cant}</td>"
                    
                    tr += f"<td>{v_p}%</td>"
                    if idx_f == 0: tr += f"<td rowspan='{len(datos_filas)+1}' class='{clase_f} score-final'>{res_final}%</td>"
                    filas_html += f"<tr>{tr}</tr>"

                f_total = f"<tr class='fila-total'><td>TOTAL</td>" + "".join([f"<td class='{'azul' if (i>0 and t<=min(totales_meses[:i])) else ('' if i==0 else 'rojo')}'>{t}</td>" for i, t in enumerate(totales_meses)]) + f"<td>{v_p}%</td></tr>"
                
                # GENERACIÓN DEL REPORTE CON VARIABLES PROCESADAS (USO DE f"")
                nombre_archivo = f"REPORTE_{suc_upper}_{mes_n.upper()}.html"
                ruta_final_html = os.path.join(ruta_suc, nombre_archivo)
                
                header_meses = "".join([f"<th>{m.upper()}</th>" for m in meses_existentes[:idx_m+1]])
                
                with open(ruta_final_html, "w", encoding="utf-8") as fr:
                    fr.write(f"""<html><head><meta charset='UTF-8'>{CSS_BASE}</head>
                    <body>
                        <img src='../../RECURSOS/logo.png' class='logo'>
                        <div class='report-container'>
                            <h1 class='report-title'>DATOS CLAVES - {suc} ({mes_n.upper()})</h1>
                            <table>
                                <thead>
                                    <tr>
                                        <th>Incidencia</th>
                                        {header_meses}
                                        <th></th>
                                        <th></th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {filas_html}
                                    {f_total}
                                </tbody>
                            </table>
                            <div class='botones-footer'>
                                <a href='../../panel.html' class='btn-volver'><i class='fas fa-home'></i> Menú Principal</a>
                            </div>
                        </div>
                    </body></html>""")

        print("\n" + "="*60 + "\n✅ TABLAS REPARADAS Y ERRORES DE RUTA SOLUCIONADOS\n" + "="*60)
    except Exception as e: 
        print(f"\n❌ ERROR: {e}")
    input("\nPresiona Enter para cerrar...")

if __name__ == "__main__": ejecutar_reportes()