import os
import time

def generar_acceso_solo_clave():
    ruta_base = os.path.dirname(os.path.abspath(__file__))
    
    # --- REPORTE EN CMD ---
    print("\n" + "="*70)
    print("      🚀 SISTEMA LUXOR - ACCESO POR CONTRASEÑA (SOLO CLAVE)")
    print("="*70)
    print(f"📁 Directorio actual: {ruta_base}")
    time.sleep(1)

    html_contenido = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Acceso - Luxor C.M.I</title>
    <style>
        body { background: #FFFFFF; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; font-family: 'Segoe UI', sans-serif; }
        .login-box { background: #0047AB; padding: 40px; border-radius: 15px; text-align: center; width: 340px; border-bottom: 8px solid #F9D908; box-shadow: 0 10px 25px rgba(0,0,0,0.2); }
        .login-box img { width: 170px; margin-bottom: 25px; }
        .login-box h2 { color: white; margin-bottom: 25px; font-size: 19px; text-transform: uppercase; }
        input { width: 100%; padding: 12px; margin-bottom: 20px; border-radius: 5px; border: none; outline: none; box-sizing: border-box; font-size: 17px; text-align: center; }
        button { width: 100%; padding: 12px; background: #F9D908; border: none; font-weight: bold; cursor: pointer; border-radius: 5px; font-size: 17px; color: #1A1D4D; }
        #error { color: #FFD7D7; display: none; margin-top: 15px; font-weight: bold; }
        #mensaje-exito { color: #90FF90; display: none; margin-top: 15px; font-weight: bold; }
    </style>
</head>
<body>

    <div class="login-box">
        <img src="RECURSOS/logo.png" alt="Luxor">
        <h2>ESTADÍSTICAS C.M.I</h2>
        
        <div id="formulario">
            <input type="password" id="pass" placeholder="Ingresa la Contraseña">
            <button onclick="validar()">INGRESAR</button>
        </div>

        <p id="error">❌ Contraseña incorrecta</p>
        <p id="mensaje-exito">✅ Acceso concedido. Entrando...</p>
    </div>

    <div id="redirector"></div>

    <script>
        function validar() {
            const p = document.getElementById('pass').value;
            
            if (p === 'Luxor-2026') {
                document.getElementById('formulario').style.display = 'none';
                document.getElementById('mensaje-exito').style.display = 'block';
                document.getElementById('error').style.display = 'none';
                
                // INYECCIÓN DE SALTO AUTOMÁTICO (Bypass de seguridad local)
                document.getElementById('redirector').innerHTML = '<meta http-equiv="refresh" content="1;url=panel.html">';
            } else {
                document.getElementById('error').style.display = 'block';
                document.getElementById('pass').value = '';
            }
        }

        // Permitir entrar con la tecla Enter
        document.getElementById('pass').addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                validar();
            }
        });
    </script>
</body>
</html>"""

    try:
        print("🛠️  Escribiendo index.html con acceso por clave única...")
        with open(os.path.join(ruta_base, "index.html"), "w", encoding="utf-8") as f:
            f.write(html_contenido)
        
        print("\n✅ PROCESO COMPLETADO CON ÉXITO:")
        print(f"   🔑 Clave configurada: Luxor-2026")
        print(f"   📂 Archivo de destino: panel.html")
        print("-" * 70)
        
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: No se pudo generar el archivo. {e}")

    print("\n👉 Presiona ENTER para finalizar y cerrar esta ventana...")
    input()

if __name__ == "__main__":
    generar_acceso_solo_clave()