import os
import time
import shutil
import json
from datetime import datetime

def generar_index_maestro_con_limpieza():
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

        print(f"📅 Mes de referencia: {meses_ordenados[mes_actual_idx].upper()}")
        print("🧹 Iniciando limpieza de carpetas fuera del rango de 6 meses...")

        for carpeta in os.listdir(ruta_raiz):
            ruta_carpeta = os.path.join(ruta_raiz, carpeta)
            if os.path.isdir(ruta_carpeta) and carpeta.lower() in meses_ordenados:
                if carpeta.lower() not in indices_a_conservar:
                    print(f"   [Eliminando]: {carpeta.upper()}")
                    shutil.rmtree(ruta_carpeta)
                else:
                    print(f"   [Manteniendo]: {carpeta.upper()}")

        print("\n🔍 Vinculando datos de ranking...")
        ranking_data_js = "{}"
        if os.path.exists(ruta_json):
            try:
                with open(ruta_json, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    ranking_data_js = json.dumps(data)
                print("   ✅ Datos reales vinculados con éxito.")
            except Exception as e:
                print(f"   ⚠️ Error al procesar JSON: {e}")
        else:
            print("   ❌ ERROR: No se encontró 'datos_ranking.json'.")

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
            print("\n⚠️ No se encontraron reportes para indexar.")
            input("\nPresiona ENTER para salir...")
            return

        ultimo_mes = list(datos_por_mes.keys())[-1]

        print(f"\n📝 Escribiendo panel.html...")
        
        html_sucursales = ""
        for mes, sucs in datos_por_mes.items():
            display = "grid" if mes == ultimo_mes else "none"
            html_sucursales += f'<div id="grupo-{mes}" class="contenedor-sucursales group-mes" style="display: {display};">\n'
            for s in sorted(sucs, key=lambda x: x['nombre']):
                html_sucursales += f'    <a href="{s["url"]}" class="card-sucursal">{s["nombre"]}</a>\n'
            html_sucursales += '</div>\n'

        botones_meses = "".join([f'<button class="btn-mes {"active" if m == ultimo_mes else ""}" onclick="cambiarMes(\'{m}\', this)">{m}</button>\n' for m in datos_por_mes.keys()])

        # AJUSTE DE ESTILO: De fixed a bloque centrado
        ranking_html = f"""
    <style>
        .btn-reporte-general {{ 
            display: block; 
            margin: 0 auto 20px auto; 
            background: #0047AB; 
            color: white; 
            border: 3px solid #F9D908; 
            padding: 12px 25px; 
            border-radius: 12px; 
            font-weight: bold; 
            cursor: pointer; 
            text-transform: uppercase; 
            box-shadow: 0 4px 10px rgba(0,0,0,0.3); 
            transition: 0.3s; 
            font-size: 0.9rem; 
        }}
        .btn-reporte-general:hover {{ background: #F9D908; color: #1A1D4D; transform: scale(1.05); }}
        .modal-ranking {{ display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); }}
        .modal-content-ranking {{ background: white; margin: 5% auto; padding: 25px; width: 380px; border-radius: 15px; border: 5px solid #1A1D4D; position: relative; }}
        .tabla-ranking {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        .tabla-ranking th {{ background: #1A1D4D; color: white; padding: 10px; text-align: left; }}
        .tabla-ranking td {{ padding: 10px; border-bottom: 1px solid #ddd; font-weight: bold; color: #1A1D4D; }}
        .close-rank {{ position: absolute; right: 15px; top: 10px; font-size: 30px; cursor: pointer; color: #E61E25; font-weight: bold; }}
    </style>

    <div id="modalRanking" class="modal-ranking">
        <div class="modal-content-ranking">
            <span class="close-rank" onclick="cerrarRanking()">&times;</span>
            <h2 style="text-align:center; color:#1A1D4D; margin:0; border-bottom: 3px solid #F9D908; padding-bottom: 10px;">Cantidad de Incidencias</h2>
            <small id="titulo-ranking-mes" style="text-align:center; display:block; color:#E61E25; font-weight:bold; margin-top:5px;"></small>
            <table class="tabla-ranking">
                <thead><tr><th>SUCURSAL</th><th style="text-align:right;">INCIDENCIAS</th></tr></thead>
                <tbody id="cuerpoRanking"></tbody>
            </table>
        </div>
    </div>

    <script>
        const DATOS_REALES = {ranking_data_js};
        function abrirRanking() {{
            const mesActual = document.getElementById('mes-titulo').innerText.toLowerCase();
            document.getElementById('titulo-ranking-mes').innerText = "MES: " + mesActual.toUpperCase();
            let lista = [];
            if (DATOS_REALES[mesActual]) {{
                Object.keys(DATOS_REALES[mesActual]).forEach(suc => {{
                    lista.push({{ nombre: suc, total: DATOS_REALES[mesActual][suc] }});
                }});
            }}
            lista.sort((a, b) => b.total - a.total);
            const cuerpo = document.getElementById('cuerpoRanking');
            if (lista.length > 0) {{
                cuerpo.innerHTML = lista.map(i => 
                    `<tr><td>${{i.nombre}}</td><td style="text-align:right; color:#E61E25;">${{i.total}}</td></tr>`
                ).join('');
            }} else {{
                cuerpo.innerHTML = '<tr><td colspan="2" style="text-align:center;">No hay datos en el JSON</td></tr>';
            }}
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
    <title>Panel Luxor</title>
    <link rel="stylesheet" href="RECURSOS/styles.css?v={version}">
    <style>
        .header-titulo {{ text-align: center; margin: 40px 0; font-family: 'Arial Black', Gadget, sans-serif; font-size: 65px; font-weight: 900; text-transform: uppercase; letter-spacing: -2px; color: #1A1D4D; -webkit-text-stroke: 2px #F9D908; text-shadow: 4px 4px 0px #0047AB, 8px 8px 15px rgba(0,0,0,0.4); line-height: 1.1; }}
        #mes-titulo {{ color: #1A1D4D; -webkit-text-stroke: 2px #F9D908; display: block; font-size: 80px; }}
        .selector-meses {{ width: 92%; max-width: 1150px; display: flex; flex-wrap: wrap; justify-content: center; gap: 10px; margin: 25px auto; padding: 20px; background: #f4f4f4; border-radius: 15px; border: 1px solid #ccc; }}
        .btn-mes {{ padding: 10px 20px; background: #1A1D4D; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; text-transform: uppercase; transition: 0.3s; }}
        .btn-mes:hover {{ background: #F9D908; color: #1A1D4D; }}
        .btn-mes.active {{ background: #F9D908; color: #1A1D4D; border: 2px solid #1A1D4D; }}
        .titulo-seccion {{ width: 100%; text-align: center; color: #1A1D4D; font-weight: 800; margin-bottom: 10px; font-size: 1.1rem; }}
    </style>
    {ranking_html}
</head>
<body>
    <header><img src="RECURSOS/logo.png" alt="LUXOR" class="logo-luxor"></header>
    <div class="header-titulo">ESTADÍSTICAS C.M.I <span id="mes-titulo">{ultimo_mes.upper()}</span></div>
    
    <button class="btn-reporte-general" onclick="abrirRanking()">📊 Total de incidencias por mes</button>

    <div class="panel-azul"><main id="main-container">{html_sucursales}</main></div>
    <div class="selector-meses"><div class="titulo-seccion">HISTORIAL DE EVALUACIONES:</div>{botones_meses}</div>
    <script>
        function cambiarMes(mes, btn) {{
            document.querySelectorAll('.group-mes').forEach(div => div.style.display = 'none');
            document.querySelectorAll('.btn-mes').forEach(b => b.classList.remove('active'));
            document.getElementById('grupo-' + mes).style.display = 'grid';
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

    except Exception as e:
        print(f"\n❌ [ERROR]: {e}")

    input("\nPresiona ENTER para finalizar...")

if __name__ == "__main__":
    generar_index_maestro_con_limpieza()