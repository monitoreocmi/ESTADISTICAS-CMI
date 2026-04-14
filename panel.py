import os
import time
import shutil
from datetime import datetime

def generar_index_maestro_con_limpieza():
    try:
        ruta_raiz = os.path.dirname(os.path.abspath(__file__))
        
        print("\n" + "="*60)
        print("🚀 INICIANDO PROCESO DE ACTUALIZACIÓN DE INDEX")
        print("="*60)

        meses_ordenados = [
            "enero", "febrero", "marzo", "abril", "mayo", "junio", 
            "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
        ]

        # 1. LÓGICA DE LIMPIEZA
        fecha_actual = datetime.now()
        mes_actual_idx = fecha_actual.month - 1
        
        indices_a_conservar = []
        for i in range(6):
            idx = (mes_actual_idx - i) % 12
            indices_a_conservar.append(meses_ordenados[idx])

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

        # 2. ESCANEO DE REPORTES
        print("\n🔍 Escaneando archivos de reporte en las carpetas conservadas...")
        datos_por_mes = {}
        for mes in meses_ordenados:
            ruta_mes = os.path.join(ruta_raiz, mes)
            if os.path.exists(ruta_mes) and os.path.isdir(ruta_mes):
                sucursales = [d for d in os.listdir(ruta_mes) if os.path.isdir(os.path.join(ruta_mes, d))]
                reportes_validos = []
                for suc in sucursales:
                    nombre_rep = f"REPORTE_{suc.upper()}_{mes.upper()}.html"
                    enlace = f"{mes}/{suc}/{nombre_rep}"
                    if os.path.exists(os.path.join(ruta_raiz, enlace)):
                        reportes_validos.append({"nombre": suc, "url": enlace})
                
                if reportes_validos:
                    print(f"   ✅ {mes.upper()}: Detectadas {len(reportes_validos)} sucursales.")
                    datos_por_mes[mes] = reportes_validos

        if not datos_por_mes:
            print("\n⚠️ No se encontraron archivos HTML para indexar.")
            input("\nPresiona ENTER para salir...")
            return

        lista_meses_disponibles = list(datos_por_mes.keys())
        ultimo_mes = lista_meses_disponibles[-1]

        # 3. CONSTRUCCIÓN DE HTML
        print(f"\n📝 Generando panel.html (Mes predeterminado: {ultimo_mes.upper()})...")
        html_sucursales = ""
        for mes, sucs in datos_por_mes.items():
            display = "grid" if mes == ultimo_mes else "none"
            html_sucursales += f'<div id="grupo-{mes}" class="contenedor-sucursales group-mes" style="display: {display};">\n'
            for s in sorted(sucs, key=lambda x: x['nombre']):
                html_sucursales += f'    <a href="{s["url"]}" class="card-sucursal">{s["nombre"]}</a>\n'
            html_sucursales += '</div>\n'

        botones_meses = ""
        for mes in datos_por_mes.keys():
            active = "active" if mes == ultimo_mes else ""
            botones_meses += f'<button class="btn-mes {active}" onclick="cambiarMes(\'{mes}\', this)">{mes}</button>\n'

        version = int(time.time())

        html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Panel Luxor</title>
    <link rel="stylesheet" href="RECURSOS/styles.css?v={version}">
    <style>
        /* Título Estilo WordArt Gigante */
        .header-titulo {{ 
            text-align: center; 
            margin: 40px 0; 
            font-family: 'Arial Black', Gadget, sans-serif;
            font-size: 65px; /* Tamaño mucho más grande */
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: -2px;
            /* Efecto WordArt: Contorno y Sombra */
            color: #1A1D4D;
            -webkit-text-stroke: 2px #F9D908;
            text-shadow: 4px 4px 0px #0047AB, 8px 8px 15px rgba(0,0,0,0.4);
            line-height: 1.1;
        }}
        
        /* El mes ahora hereda el mismo color y estilo que el título principal */
        #mes-titulo {{ 
            color: #1A1D4D; 
            -webkit-text-stroke: 2px #F9D908;
            display: block; /* Salto de línea para mayor impacto */
            font-size: 80px;
        }}
        
        .selector-meses {{ 
            width: 92%; 
            max-width: 1150px; 
            display: flex; 
            flex-wrap: wrap; 
            justify-content: center; 
            gap: 10px; 
            margin: 25px auto; 
            padding: 20px; 
            background: #f4f4f4; 
            border-radius: 15px; 
            border: 1px solid #ccc; 
        }}
        .btn-mes {{ padding: 10px 20px; background: #1A1D4D; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; text-transform: uppercase; transition: 0.3s; }}
        .btn-mes:hover {{ background: #F9D908; color: #1A1D4D; }}
        .btn-mes.active {{ background: #F9D908; color: #1A1D4D; border: 2px solid #1A1D4D; }}
        .titulo-seccion {{ width: 100%; text-align: center; color: #1A1D4D; font-weight: 800; margin-bottom: 10px; font-size: 1.1rem; }}
    </style>
</head>
<body>
    <header><img src="RECURSOS/logo.png" alt="LUXOR" class="logo-luxor"></header>
    
    <div class="header-titulo">
        ESTADÍSTICAS C.M.I 
        <span id="mes-titulo">{ultimo_mes.upper()}</span>
    </div>

    <div class="panel-azul">
        <main id="main-container">
            {html_sucursales}
        </main>
    </div>

    <div class="selector-meses">
        <div class="titulo-seccion">HISTORIAL DE EVALUACIONES:</div>
        {botones_meses}
    </div>

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
            f.write(html_content)

        print("\n" + "="*60)
        print("✨ INDEX ACTUALIZADO EXITOSAMENTE")
        print("="*60)

    except Exception as e:
        print(f"\n❌ [ERROR]: {e}")

    input("\nPresiona ENTER para finalizar...")

if __name__ == "__main__":
    generar_index_maestro_con_limpieza()