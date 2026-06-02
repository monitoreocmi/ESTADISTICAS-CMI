import os
import time
import shutil
import json
from datetime import datetime

def generar_index_maestro_con_limpieza():
    # Inicializamos variables para evitar errores de "not defined"
    html_sucursales = ""
    botones_meses = ""
    ultimo_mes = ""
    
    try:
        ruta_raiz = os.path.dirname(os.path.abspath(__file__))
        ruta_json = os.path.join(ruta_raiz, "datos_ranking.json")
        
        print("\n" + "="*60)
        print("🚀 INICIANDO PROCESO DE ACTUALIZACIÓN DE INDEX")
        print("="*60)

        meses_ordenados = ["enero", "febrero", "marzo", "abril", "mayo", "junio", 
                           "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

        fecha_actual = datetime.now()
        mes_actual_idx = fecha_actual.month - 1
        indices_a_conservar = [meses_ordenados[(mes_actual_idx - i) % 12] for i in range(6)]

        # 1. LIMPIEZA DE CARPETAS
        for carpeta in os.listdir(ruta_raiz):
            ruta_carpeta = os.path.join(ruta_raiz, carpeta)
            if os.path.isdir(ruta_carpeta) and carpeta.lower() in meses_ordenados:
                if carpeta.lower() not in indices_a_conservar:
                    shutil.rmtree(ruta_carpeta)

        # 2. CARGAR DATOS DEL RANKING
        ranking_data_js = "{}"
        if os.path.exists(ruta_json):
            try:
                with open(ruta_json, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    ranking_data_js = json.dumps(data)
            except: pass

        # 3. ESCANEO DE REPORTES Y GENERACIÓN DE LINKS
        datos_por_mes = {}
        for mes in meses_ordenados:
            ruta_mes = os.path.join(ruta_raiz, mes)
            if os.path.exists(ruta_mes) and os.path.isdir(ruta_mes):
                sucursales = [d for d in os.listdir(ruta_mes) if os.path.isdir(os.path.join(ruta_mes, d))]
                reportes_validos = []
                for suc in sucursales:
                    nombre_rep = f"REPORTE_{suc.upper()}_{mes.upper()}.html"
                    if os.path.exists(os.path.join(ruta_mes, suc, nombre_rep)):
                        reportes_validos.append({"nombre": suc, "url": f"{mes}/{suc}/{nombre_rep}"})
                if reportes_validos:
                    datos_por_mes[mes] = reportes_validos

        if not datos_por_mes:
            print("⚠️ No se encontraron reportes. Revisa las carpetas de los meses.")
            input("Presiona ENTER para salir...")
            return

        ultimo_mes = list(datos_por_mes.keys())[-1]
        
        # Mapa de URLs para el ranking dinámico
        urls_reportes = {}
        for mes, sucs in datos_por_mes.items():
            urls_reportes[mes] = {s['nombre'].upper(): s['url'] for s in sucs}
        urls_js = json.dumps(urls_reportes)

        # Generar bloques de sucursales
        for mes, sucs in datos_por_mes.items():
            display = "grid" if mes == ultimo_mes else "none"
            html_sucursales += f'<div id="grupo-{mes}" class="contenedor-sucursales group-mes" style="display: {display};">\n'
            for s in sorted(sucs, key=lambda x: x['nombre']):
                html_sucursales += f'    <a href="{s["url"]}" class="card-sucursal">{s["nombre"]}</a>\n'
            html_sucursales += '</div>\n'

        botones_meses = "".join([f'<button class="btn-mes {"active" if m == ultimo_mes else ""}" onclick="cambiarMes(\'{m}\', this)">{m}</button>\n' for m in datos_por_mes.keys()])

        ranking_html = f"""
    <style>
        .btn-reporte-general {{ 
            display: block; margin: 0 auto 20px auto; background: #0047AB; color: white; 
            border: 3px solid #F9D908; padding: 12px 25px; border-radius: 12px; 
            font-weight: bold; cursor: pointer; text-transform: uppercase; 
            box-shadow: 0 4px 10px rgba(0,0,0,0.3); transition: 0.3s; font-size: 0.9rem; 
        }}
        .modal-ranking {{ display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); overflow-y: auto; }}
        .modal-content-ranking {{ background: white; margin: 5% auto; padding: 25px; width: 90%; max-width: 400px; border-radius: 15px; border: 5px solid #1A1D4D; position: relative; }}
        .tabla-ranking {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        .tabla-ranking th {{ background: #1A1D4D; color: white; padding: 10px; text-align: left; font-size: 0.8rem; }}
        .tabla-ranking td {{ padding: 10px; border-bottom: 1px solid #ddd; font-weight: bold; color: #1A1D4D; }}
        .link-incidencia {{ color: #E61E25; text-decoration: none; font-weight: bold; padding: 5px; display: block; text-align: right; }}
        .link-incidencia:hover {{ background: #f0f0f0; border-radius: 5px; }}
        .close-rank {{ position: absolute; right: 15px; top: 10px; font-size: 30px; cursor: pointer; color: #E61E25; font-weight: bold; }}
    </style>

    <div id="modalRanking" class="modal-ranking">
        <div class="modal-content-ranking">
            <span class="close-rank" onclick="cerrarRanking()">&times;</span>
            <h2 style="text-align:center; color:#1A1D4D; margin:0; font-size:1.2rem; border-bottom: 3px solid #F9D908; padding-bottom: 10px;">Cantidad de Incidencias</h2>
            <small id="titulo-ranking-mes" style="text-align:center; display:block; color:#E61E25; font-weight:bold; margin-top:5px;"></small>
            <table class="tabla-ranking">
                <thead><tr><th>SUCURSAL</th><th style="text-align:right;">PUNTOS</th></tr></thead>
                <tbody id="cuerpoRanking"></tbody>
            </table>
        </div>
    </div>

    <script>
        const DATOS_REALES = {ranking_data_js};
        const URLS_REPORTES = {urls_js};

        function abrirRanking() {{
            const mesActual = document.getElementById('mes-titulo').innerText.toLowerCase();
            document.getElementById('titulo-ranking-mes').innerText = "MES SELECCIONADO: " + mesActual.toUpperCase();
            let lista = [];
            if (DATOS_REALES[mesActual]) {{
                Object.keys(DATOS_REALES[mesActual]).forEach(suc => {{
                    lista.push({{ nombre: suc, total: DATOS_REALES[mesActual][suc] }});
                }});
            }}
            lista.sort((a, b) => b.total - a.total);
            const cuerpo = document.getElementById('cuerpoRanking');
            cuerpo.innerHTML = lista.map(i => {{
                const url = URLS_REPORTES[mesActual] ? URLS_REPORTES[mesActual][i.nombre] : '#';
                return `<tr>
                    <td>${{i.nombre}}</td>
                    <td style="text-align:right;">
                        <a href="${{url}}" class="link-incidencia" title="Ver Reporte">${{i.total}}</a>
                    </td>
                </tr>`;
            }}).join('');
            document.getElementById('modalRanking').style.display = "block";
        }}
        function cerrarRanking() {{ document.getElementById('modalRanking').style.display = "none"; }}
    </script>
        """

        version = int(time.time())
        html_final = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Panel Luxor</title>
    <link rel="stylesheet" href="RECURSOS/styles.css?v={version}">
    <style>
        /* DISEÑO RESPONSIVO PARA TÍTULOS */
        .header-titulo {{ 
            text-align: center; margin: 20px 0; font-family: 'Arial Black', sans-serif; 
            font-weight: 900; text-transform: uppercase; color: #1A1D4D; 
            -webkit-text-stroke: 1.5px #F9D908; text-shadow: 3px 3px 0px #0047AB;
            line-height: 1.1; font-size: clamp(24px, 7vw, 60px); 
        }}
        #mes-titulo {{ 
            display: block; color: #1A1D4D; -webkit-text-stroke: 1.5px #F9D908;
            font-size: clamp(32px, 10vw, 75px);
        }}
        
        @media (max-width: 600px) {{
            .header-titulo {{ margin: 15px 5px; }}
            .btn-reporte-general {{ width: 95%; font-size: 0.8rem; padding: 12px; }}
            .logo-luxor {{ max-width: 150px !important; }}
        }}

        .selector-meses {{ width: 92%; max-width: 1150px; display: flex; flex-wrap: wrap; justify-content: center; gap: 8px; margin: 20px auto; padding: 15px; background: #f4f4f4; border-radius: 15px; border: 1px solid #ccc; }}
        .btn-mes {{ padding: 8px 16px; background: #1A1D4D; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; text-transform: uppercase; font-size: 0.8rem; }}
        .btn-mes.active {{ background: #F9D908; color: #1A1D4D; border: 2px solid #1A1D4D; }}
        .titulo-seccion {{ width: 100%; text-align: center; color: #1A1D4D; font-weight: 800; margin-bottom: 8px; font-size: 1rem; }}
    </style>
    {ranking_html}
</head>
<body>
    <header style="padding: 10px 0;"><img src="RECURSOS/logo.png" alt="LUXOR" class="logo-luxor" style="max-width:200px; display:block; margin:auto;"></header>
    
    <div class="header-titulo">ESTADÍSTICAS C.M.I <span id="mes-titulo">{ultimo_mes.upper()}</span></div>
    
    <button class="btn-reporte-general" onclick="abrirRanking()">📊 Total de incidencias por mes</button>

    <div class="panel-azul"><main id="main-container">{html_sucursales}</main></div>
    
    <div class="selector-meses">
        <div class="titulo-seccion">HISTORIAL DE EVALUACIONES:</div>
        {botones_meses}
    </div>

    <script>
        function cambiarMes(mes, btn) {{
            document.querySelectorAll('.group-mes').forEach(div => div.style.display = 'none');
            document.querySelectorAll('.btn-mes').forEach(b => b.classList.remove('active'));
            const target = document.getElementById('grupo-' + mes);
            if(target) target.style.display = 'grid';
            btn.classList.add('active');
            document.getElementById('mes-titulo').innerText = mes.toUpperCase();
        }}
    </script>
</body>
</html>"""

        with open(os.path.join(ruta_raiz, "panel.html"), "w", encoding="utf-8") as f:
            f.write(html_final)
            
        print("\n" + "="*60)
        print("✨ INDEX ACTUALIZADO EXITOSAMENTE")
        print("="*60)

    except PermissionError:
        print("\n❌ [ERROR]: No se pudo escribir 'panel.html'.")
        print("Cierra el archivo si lo tienes abierto en el navegador o editor y reintenta.")
    except Exception as e:
        print(f"\n❌ [ERROR]: {e}")

    input("\nPresiona ENTER para finalizar...")

if __name__ == "__main__":
    generar_index_maestro_con_limpieza()