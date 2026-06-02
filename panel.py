import os
import time
import shutil
import json
from datetime import datetime

def generar_index_maestro_con_limpieza():
    version = int(time.time())
    html_sucursales_mensual = ""
    html_sucursales_semanal = ""
    botones_meses = ""
    ultimo_mes = ""
    ranking_data_js = "{}"
    
    try:
        ruta_raiz = os.path.dirname(os.path.abspath(__file__))
        ruta_json = os.path.join(ruta_raiz, "datos_ranking.json")
        
        print("\n" + "="*60 + "\n🚀 ACTUALIZANDO PANEL MAESTRO CON PESTAÑAS DINÁMICAS\n" + "="*60)

        meses_ordenados = ["enero", "febrero", "marzo", "abril", "mayo", "junio", 
                           "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

        fecha_actual = datetime.now()
        mes_actual_idx = fecha_actual.month - 1
        indices_a_conservar = [meses_ordenados[(mes_actual_idx - i) % 12] for i in range(6)]

        for carpeta in os.listdir(ruta_raiz):
            ruta_carpeta = os.path.join(ruta_raiz, carpeta)
            if os.path.isdir(ruta_carpeta) and carpeta.lower() in meses_ordenados:
                if carpeta.lower() not in indices_a_conservar:
                    shutil.rmtree(ruta_carpeta)

        if os.path.exists(ruta_json):
            try:
                with open(ruta_json, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    ranking_data_js = json.dumps(data)
            except: pass

        datos_por_mes = {}
        for mes in meses_ordenados:
            ruta_mes = os.path.join(ruta_raiz, mes)
            if os.path.exists(ruta_mes) and os.path.isdir(ruta_mes):
                sucursales = [d for d in os.listdir(ruta_mes) if os.path.isdir(os.path.join(ruta_mes, d))]
                reportes_validos = []
                for suc in sucursales:
                    nombre_rep = f"REPORTE_{suc.upper()}_{mes.upper()}.html"
                    if os.path.exists(os.path.join(ruta_mes, suc, nombre_rep)):
                        reportes_validos.append({"nombre": suc, "upper": suc.upper()})
                if reportes_validos:
                    datos_por_mes[mes] = reportes_validos

        if not datos_por_mes:
            print("⚠️ No se encontraron reportes creados.")
            input("Presiona ENTER para salir...")
            return

        ultimo_mes = list(datos_por_mes.keys())[-1]
        
        for mes, sucs in datos_por_mes.items():
            display = "grid" if mes == ultimo_mes else "none"
            html_sucursales_mensual += f'<div id="grupo-men-{mes}" class="contenedor-sucursales group-mes-men" style="display: {display};">\n'
            for s in sorted(sucs, key=lambda x: x['nombre']):
                url_m = f"{mes}/{s['nombre']}/REPORTE_{s['upper']}_{mes.upper()}.html"
                html_sucursales_mensual += f'    <a href="{url_m}" class="card-sucursal" data-sucursal="{s["upper"]}">{s["nombre"]}</a>\n'
            html_sucursales_mensual += '</div>\n'

        for mes, sucs in datos_por_mes.items():
            display = "grid" if mes == ultimo_mes else "none"
            html_sucursales_semanal += f'<div id="grupo-sem-{mes}" class="contenedor-sucursales group-mes-sem" style="display: {display};">\n'
            for s in sorted(sucs, key=lambda x: x['nombre']):
                html_sucursales_semanal += f'    <a href="#" id="link-sem-{mes}-{s["upper"]}" class="card-sucursal card-suc-sem" data-mes="{mes}" data-sucursal="{s["upper"]}">{s["nombre"]}</a>\n'
            html_sucursales_semanal += '</div>\n'

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

        function abrirRanking() {{
            const mesActual = document.getElementById('mes-titulo').innerText.toLowerCase();
            document.getElementById('titulo-ranking-mes').innerText = "MES SELECCIONADO: " + mesActual.toUpperCase();
            let lista = [];
            
            if (DATOS_REALES[mesActual] && DATOS_REALES[mesActual]["mensual"]) {{
                Object.keys(DATOS_REALES[mesActual]["mensual"]).forEach(suc => {{
                    lista.push({{ nombre: suc, total: DATOS_REALES[mesActual]["mensual"][suc] }});
                }});
            }}
            lista.sort((a, b) => b.total - a.total);
            const cuerpo = document.getElementById('cuerpoRanking');
            cuerpo.innerHTML = lista.map(i => {{
                const url = `${{mesActual}}/${{i.nombre.toLowerCase()}}/REPORTE_${{i.nombre}}_${{mesActual.toUpperCase()}}.html`;
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

        html_plantilla = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Panel Luxor</title>
    <link rel="stylesheet" href="RECURSOS/styles.css?v={version}">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        .header-titulo {{ text-align: center; margin: 20px 0; font-family: 'Arial Black', sans-serif; font-weight: 900; text-transform: uppercase; color: #1A1D4D; -webkit-text-stroke: 1.5px #F9D908; text-shadow: 3px 3px 0px #0047AB; line-height: 1.1; font-size: clamp(24px, 7vw, 60px); }}
        #mes-titulo {{ display: block; color: #1A1D4D; -webkit-text-stroke: 1.5px #F9D908; font-size: clamp(32px, 10vw, 75px); }}
        .selector-meses {{ width: 92%; max-width: 1400px; display: flex; flex-wrap: wrap; justify-content: center; gap: 8px; margin: 20px auto; padding: 15px; background: #f4f4f4; border-radius: 15px; border: 1px solid #ccc; }}
        .btn-mes {{ padding: 8px 16px; background: #1A1D4D; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; text-transform: uppercase; font-size: 0.8rem; }}
        .btn-mes.active {{ background: #F9D908; color: #1A1D4D; border: 2px solid #1A1D4D; }}
        .titulo-seccion {{ width: 100%; text-align: center; color: #1A1D4D; font-weight: 800; margin-bottom: 8px; font-size: 1rem; }}
        .tabs-container {{ display: flex; justify-content: center; gap: 15px; margin: 20px 0; }}
        .tab-btn {{ background: #e0e0e0; color: #1A1D4D; border: 2px solid #1A1D4D; padding: 10px 25px; border-radius: 20px; font-weight: bold; cursor: pointer; text-transform: uppercase; font-size: 0.85rem; }}
        .tab-btn.active {{ background: #1A1D4D; color: white; }}
        .semanas-subselector {{ display: flex; justify-content: center; flex-wrap: wrap; gap: 10px; padding: 10px; margin-bottom: 15px; background: rgba(255,255,255,0.1); border-radius: 10px; width: 100%; }}
        .btn-semana {{ background: #1A1D4D; color: white; border: 2px solid white; padding: 8px 15px; font-weight: bold; border-radius: 5px; cursor: pointer; font-size: 0.8rem; text-transform: uppercase; }}
        .btn-semana.active {{ background: #F9D908; color: #1A1D4D; border-color: #1A1D4D; }}
        .porcentaje-card {{ display: block; font-size: 1.4rem; font-weight: 900; margin-top: 5px; text-shadow: 1px 1px 2px rgba(0,0,0,0.4); }}
        
        .distribucion-panel {{ display: grid; grid-template-columns: 320px 1fr 320px; gap: 20px; width: 100%; align-items: start; }}
        @media (max-width: 1200px) {{
            .distribucion-panel {{ grid-template-columns: 1fr; }}
        }}
        
        .columna-grafico {{ background: white; border-radius: 15px; padding: 15px; border: 3px solid #1A1D4D; box-shadow: 0 4px 10px rgba(0,0,0,0.1); display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 380px; }}
        .titulo-grafico {{ font-family: 'Arial', sans-serif; font-weight: bold; color: #1A1D4D; text-align: center; margin-bottom: 10px; text-transform: uppercase; font-size: 0.9rem; border-bottom: 2px solid #F9D908; padding-bottom: 5px; width: 100%; }}
        
        .columna-ranking-lateral {{ background: white; border-radius: 15px; padding: 15px; border: 3px solid #1A1D4D; box-shadow: 0 4px 10px rgba(0,0,0,0.1); max-height: 550px; overflow-y: auto; }}
        .titulo-ranking-lateral {{ font-family: 'Arial', sans-serif; font-weight: bold; color: #E61E25; text-align: center; margin-bottom: 10px; text-transform: uppercase; font-size: 0.95rem; border-bottom: 2px solid #1A1D4D; padding-bottom: 5px; }}
        .lista-ranking-lateral {{ list-style: none; padding: 0; margin: 0; }}
        .item-ranking-lateral {{ display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; border-bottom: 1px solid #eee; font-weight: bold; color: #1A1D4D; font-size: 0.85rem; transition: background 0.2s; }}
        .item-ranking-lateral:hover {{ background: #f9f9f9; }}
        .badge-incidencias {{ background: #E61E25; color: white; border-radius: 20px; padding: 3px 10px; font-size: 0.8rem; min-width: 35px; text-align: center; }}
        .posicion-ranking {{ color: #888; margin-right: 8px; font-size: 0.75rem; width: 18px; display: inline-block; }}
    </style>
    {ranking_html}
</head>
<body>
    <header style="padding: 10px 0;"><img src="RECURSOS/logo.png" alt="LUXOR" class="logo-luxor" style="max-width:200px; display:block; margin:auto;"></header>
    
    <div class="header-titulo">ESTADÍSTICAS C.M.I <span id="mes-titulo">{ultimo_mes.upper()}</span></div>
    
    <button class="btn-reporte-general" onclick="abrirRanking()">📊 Total de incidencias por mes</button>

    <div class="tabs-container">
        <button id="tab-men" class="tab-btn active" onclick="cambiarVista('mensual')">📅 Evaluacion Mensual</button>
        <button id="tab-sem" class="tab-btn" onclick="cambiarVista('semanal')">📊 Evaluacion Semanal</button>
    </div>

    <div id="contenedor-mensual" class="panel-azul">
        <div class="distribucion-panel">
            <div class="columna-grafico">
                <div class="titulo-grafico" id="titulo-grafico-men">Comparativa vs Mes Anterior</div>
                <div style="position: relative; width: 100%; height: 280px;">
                    <canvas id="chartMensual"></canvas>
                </div>
            </div>
            
            <main id="main-container-mensual">{html_sucursales_mensual}</main>
            
            <div class="columna-ranking-lateral">
                <div class="titulo-ranking-lateral">Incidencias del Mes</div>
                <ul class="lista-ranking-lateral" id="ranking-lateral-mensual"></ul>
            </div>
        </div>
    </div>
    
    <div id="contenedor-semanal" class="panel-azul" style="display:none;">
        <div class="semanas-subselector">
            <button class="btn-semana active" onclick="seleccionarSemana('semana1', this)">Semana 1</button>
            <button class="btn-semana" onclick="seleccionarSemana('semana2', this)">Semana 2</button>
            <button class="btn-semana" onclick="seleccionarSemana('semana3', this)">Semana 3</button>
            <button class="btn-semana" onclick="seleccionarSemana('semana4', this)">Semana 4</button>
            <button class="btn-semana" onclick="seleccionarSemana('semana5', this)">Semana 5</button>
        </div>
        
        <div class="distribucion-panel">
            <div class="columna-grafico">
                <div class="titulo-grafico" id="titulo-grafico-sem">Comparativa vs Semana Anterior</div>
                <div style="position: relative; width: 100%; height: 280px;">
                    <canvas id="chartSemanal"></canvas>
                </div>
            </div>
            
            <main id="main-container-semanal">{html_sucursales_semanal}</main>
            
            <div class="columna-ranking-lateral">
                <div class="titulo-ranking-lateral" id="titulo-ranking-lateral-sem">Incidencias de la Semana</div>
                <ul class="lista-ranking-lateral" id="ranking-lateral-semanal"></ul>
            </div>
        </div>
    </div>
    
    <div class="selector-meses">
        <div class="titulo-seccion">HISTORIAL DE EVALUACIONES:</div>
        {botones_meses}
    </div>

    <script>
        let modoActual = 'mensual';
        let semanaActual = 'semana1';
        let miChartMensual = null;
        let miChartSemanal = null;

        const mesesOrdenadosLista = ["enero", "febrero", "marzo", "abril", "mayo", "junio", 
                                     "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"];

        function obtenerMesAnterior(mesActual) {{
            let idx = mesesOrdenadosLista.indexOf(mesActual.toLowerCase());
            if (idx <= 0) return mesesOrdenadosLista[0];
            return mesesOrdenadosLista[idx - 1];
        }}

        function actualizarGraficoYRankingMensual() {{
            const mesAct = document.getElementById('mes-titulo').innerText.toLowerCase();
            const mesAnt = obtenerMesAnterior(mesAct);
            
            let listaSucs = [];
            if (DATOS_REALES[mesAct] && DATOS_REALES[mesAct]["mensual"]) {{
                Object.keys(DATOS_REALES[mesAct]["mensual"]).forEach(suc => {{
                    listaSucs.push({{ nombre: suc, total: DATOS_REALES[mesAct]["mensual"][suc] }});
                }});
            }}
            listaSucs.sort((a, b) => b.total - a.total);
            
            const ulRanking = document.getElementById('ranking-lateral-mensual');
            if (listaSucs.length === 0) {{
                ulRanking.innerHTML = '<li class="item-ranking-lateral" style="justify-content:center;color:#888;">Sin incidencias registradas</li>';
            }} else {{
                ulRanking.innerHTML = listaSucs.map((s, index) => `
                    <li class="item-ranking-lateral">
                        <span><span class="posicion-ranking">#\${{index+1}}</span>\${{s.nombre}}</span>
                        <span class="badge-incidencias">\${{s.total}}</span>
                    </li>
                `).join('');
            }}

            let totalIncidenciasMesActual = listaSucs.reduce((acc, current) => acc + current.total, 0);
            let totalIncidenciasMesAnterior = 0;
            if (DATOS_REALES[mesAnt] && DATOS_REALES[mesAnt]["mensual"]) {{
                Object.keys(DATOS_REALES[mesAnt]["mensual"]).forEach(suc => {{
                    totalIncidenciasMesAnterior += DATOS_REALES[mesAnt]["mensual"][suc];
                }});
            }}

            document.getElementById('titulo-grafico-men').innerText = `Comparativa Incidencias Totales`;

            const ctx = document.getElementById('chartMensual').getContext('2d');
            if (miChartMensual) {{
                miChartMensual.destroy();
            }}
            
            miChartMensual = new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: [mesAnt.toUpperCase(), mesAct.toUpperCase()],
                    datasets: [{{
                        label: 'Incidencias Totales',
                        data: [totalIncidenciasMesAnterior, totalIncidenciasMesActual],
                        backgroundColor: ['#00B0F0', '#E61E25'],
                        borderWidth: 1,
                        borderRadius: 5
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{ display: false }}
                    }},
                    scales: {{
                        y: {{ beginAtZero: true, ticks: {{ precision: 0 }} }}
                    }}
                }}
            }});
        }

        function actualizarGraficoYRankingSemanal() {{
            const mesAct = document.getElementById('mes-titulo').innerText.toLowerCase();
            const numSemanaActual = parseInt(semanaActual.replace('semana', ''));
            const numSemanaAnterior = numSemanaActual > 1 ? numSemanaActual - 1 : 1;
            const semanaAntLabel = 'semana' + numSemanaAnterior;

            document.getElementById('titulo-ranking-lateral-sem').innerText = `Incidencias: Semana \${{numSemanaActual}}`;
            document.getElementById('titulo-grafico-sem').innerText = `Comparativa Sem. \${{numSemanaAnterior}} vs Sem. \${{numSemanaActual}}`;

            const dataMes = DATOS_REALES[mesAct] || {{}};
            const dataSemanas = dataMes.semanas_incidencias || dataMes.semanas || {{}}; 
            
            let incidenciasSemanaActual = dataSemanas[semanaActual] || {{}};
            let incidenciasSemanaAnterior = dataSemanas[semanaAntLabel] || {{}};

            let listaSucsSem = [];
            Object.keys(incidenciasSemanaActual).forEach(suc => {{
                let valor = incidenciasSemanaActual[suc];
                if (typeof valor === 'object' && valor !== null) {{
                    valor = valor.incidencias || 0;
                }}
                listaSucsSem.push({{ nombre: suc, total: Number(valor) || 0 }}):
            }});
            
            if (listaSucsSem.length === 0) {{
                const tarjetas = document.querySelectorAll(`#grupo-sem-\${{mesAct}} .card-suc-sem`);
                tarjetas.forEach(t => {{
                    listaSucsSem.push({{ nombre: t.getAttribute('data-sucursal'), total: 0 }});
                }});
            }}
            
            listaSucsSem.sort((a, b) => b.total - a.total);

            const ulRankingSem = document.getElementById('ranking-lateral-semanal');
            ulRankingSem.innerHTML = listaSucsSem.map((s, index) => `
                <li class="item-ranking-lateral">
                    <span><span class="posicion-ranking">#\${{index+1}}</span>\${{s.nombre}}</span>
                    <span class="badge-incidencias">\text{\${{s.total}}}</span>
                </li>
            `).join('');

            let totalSemAct = listaSucsSem.reduce((acc, curr) => acc + curr.total, 0);
            let totalSemAnt = 0;
            
            Object.keys(incidenciasSemanaAnterior).forEach(suc => {{
                let val = incidenciasSemanaAnterior[suc];
                if (typeof val === 'object' && val !== null) val = val.incidencias || 0;
                totalSemAnt += Number(val) || 0;
            }});

            const ctxSem = document.getElementById('chartSemanal').getContext('2d');
            if (miChartSemanal) {{
                miChartSemanal.destroy();
            }}

            miChartSemanal = new Chart(ctxSem, {{
                type: 'bar',
                data: {{
                    labels: [`Semana \${{numSemanaAnterior}}`, `Semana \${{numSemanaActual}}`],
                    datasets: [{{
                        label: 'Incidencias Totales',
                        data: [totalSemAnt, totalSemAct],
                        backgroundColor: ['#0047AB', '#F9D908'],
                        borderWidth: 1,
                        borderRadius: 5
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{ display: false }}
                    }},
                    scales: {{
                        y: {{ beginAtZero: true, ticks: {{ precision: 0 }} }}
                    }}
                }}
            }});
        }

        function cambiarMes(mes, btn) {{
            document.querySelectorAll('.btn-mes').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById('mes-titulo').innerText = mes.toUpperCase();
            
            document.querySelectorAll('.group-mes-men').forEach(div => div.style.display = 'none');
            document.querySelectorAll('.group-mes-sem').forEach(div => div.style.display = 'none');
            
            if(modoActual === 'mensual') {{
                const target = document.getElementById('grupo-men-' + mes);
                if(target) target.style.display = 'grid';
                actualizarGraficoYRankingMensual();
            }} else {{
                const target = document.getElementById('grupo-sem-' + mes);
                if(target) target.style.display = 'grid';
                renderizarEstructuraSemanales();
                actualizarGraficoYRankingSemanal();
            }}
        }}

        function cambiarVista(modo) {{
            modoActual = modo;
            document.getElementById('tab-men').classList.remove('active');
            document.getElementById('tab-sem').classList.remove('active');
            
            const mesAct = document.getElementById('mes-titulo').innerText.toLowerCase();
            document.querySelectorAll('.group-mes-men').forEach(div => div.style.display = 'none');
            document.querySelectorAll('.group-mes-sem').forEach(div => div.style.display = 'none');

            if(modo === 'mensual') {{
                document.getElementById('tab-men').classList.add('active');
                document.getElementById('contenedor-mensual').style.display = 'block';
                document.getElementById('contenedor-semanal').style.display = 'none';
                const target = document.getElementById('grupo-men-' + mesAct);
                if(target) target.style.display = 'grid';
                actualizarGraficoYRankingMensual();
            }} else {{
                document.getElementById('tab-sem').classList.add('active');
                document.getElementById('contenedor-mensual').style.display = 'none';
                document.getElementById('contenedor-semanal').style.display = 'block';
                const target = document.getElementById('grupo-sem-' + mesAct);
                if(target) target.style.display = 'grid';
                renderizarEstructuraSemanales();
                actualizarGraficoYRankingSemanal();
            }}
        }}

        function seleccionarSemana(semana, btn) {{
            document.querySelectorAll('.btn-semana').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            semanaActual = semana;
            renderizarEstructuraSemanales();
            actualizarGraficoYRankingSemanal();
        }}

        function renderizarEstructuraSemanales() {{
            const mesAct = document.getElementById('mes-titulo').innerText.toLowerCase();
            const dataMes = DATOS_REALES[mesAct] || {{}};
            const dataSemanas = dataMes.semanas || {{}};
            const scoreSemana = dataSemanas[semanaActual] || {{}};

            const tarjetas = document.querySelectorAll(`#grupo-sem-\${{mesAct}} .card-suc-sem`);
            tarjetas.forEach(tarjeta => {{
                const sucUpper = tarjeta.getAttribute('data-sucursal');
                const score = scoreSemana[sucUpper] !== undefined ? scoreSemana[sucUpper] : 100;
                
                tarjeta.href = `\${{mesAct}}/\${{sucUpper.toLowerCase()}}/REPORTE_\${{sucUpper}}_\${{mesAct.toUpperCase()}}_\${{semanaActual.toUpperCase()}}.html`;
                tarjeta.innerHTML = `\${{sucUpper.toLowerCase()}} <span class="porcentaje-card">\${{score}}%</span>`;
                
                if(score >= 70) {{
                    tarjeta.style.background = "#00B0F0";
                    tarjeta.style.color = "white";
                }} else {{
                    tarjeta.style.background = "#E61E25";
                    tarjeta.style.color = "white";
                }}
            }});
        }}

        document.addEventListener("DOMContentLoaded", () => {{
            actualizarGraficoYRankingMensual();
            if(modoActual === 'semanal') {{
                renderizarEstructuraSemanales();
                actualizarGraficoYRankingSemanal();
            }}
        }});

    </script>
</body>
</html>"""

        with open(os.path.join(ruta_raiz, "panel.html"), "w", encoding="utf-8") as f:
            f.write(html_plantilla)
            
        print("✨ INDEX ACTUALIZADO EXITOSAMENTE CON CONTENEDORES LATERALES DINÁMICOS (panel.html)")

    except Exception as e:
        print(f"\n❌ [ERROR]: {e}")
    input("\nPresiona ENTER para finalizar...")

if __name__ == "__main__":
    generar_index_maestro_con_limpieza()