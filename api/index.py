# api/index.py

from flask import Flask, request, render_template_string, send_file
import io
import os
import sys
from datetime import datetime # Importante para convertir la fecha del input nativo

# --- INICIO: Lógica para resolver importaciones ---
base_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(base_dir, '..')
sys.path.insert(0, project_root)
from rol_automator import generar_excel_desde_texto
# --- FIN: Lógica para resolver importaciones ---

app = Flask(__name__)

# --- INICIO DEL FRONTEND (ESTILO APPLE / PREMIUM DARK) ---
HTML_TEMPLATE = """
<!doctype html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Generador de Rol</title>
    
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    
    <style>
        :root {
            /* Paleta Premium Dark (Apple/Material Monochrome) */
            --bg-body: #000000;         /* Negro puro */
            --bg-card: #1c1c1e;         /* Gris oscuro secundario (iOS Surface) */
            --bg-input: #2c2c2e;        /* Gris terciario para inputs */
            --bg-input-focus: #3a3a3c;
            
            --text-primary: #ffffff;
            --text-secondary: #8e8e93;  /* Gris Apple */
            
            --accent-color: #ffffff;    /* Acento blanco para alto contraste */
            --border-radius: 18px;      /* Bordes redondeados modernos */
            --btn-radius: 99px;         /* Botón tipo píldora */
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: var(--bg-body);
            color: var(--text-primary);
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
            -webkit-font-smoothing: antialiased;
        }

        .container {
            background-color: var(--bg-card);
            border-radius: var(--border-radius);
            padding: 40px;
            max-width: 580px;
            width: 100%;
            box-shadow: 0 20px 40px rgba(0,0,0,0.4); /* Sombra suave y profunda */
        }

        h1 {
            font-size: 1.8rem;
            font-weight: 600;
            margin: 0 0 10px 0;
            text-align: center;
            letter-spacing: -0.5px;
        }

        .subtitle {
            text-align: center;
            color: var(--text-secondary);
            margin-bottom: 40px;
            font-size: 1rem;
            font-weight: 400;
        }

        /* Formulario */
        .form-group {
            margin-bottom: 24px;
        }

        label {
            display: block;
            font-weight: 500;
            font-size: 0.9rem;
            margin-bottom: 10px;
            color: var(--text-secondary);
            margin-left: 4px; /* Pequeño indent visual */
        }

        /* Inputs Estilo iOS/Android Moderno: Sin bordes, solo fondo */
        textarea, input[type="date"] {
            width: 100%;
            padding: 16px;
            background-color: var(--bg-input);
            border: 1px solid transparent; /* Transparente por defecto */
            border-radius: 14px;
            font-family: inherit;
            font-size: 1rem;
            color: var(--text-primary);
            transition: all 0.2s ease;
            box-sizing: border-box;
            appearance: none; /* Quita estilos nativos feos */
        }
        
        /* Ajuste específico para el selector de fecha en modo oscuro */
        input[type="date"]::-webkit-calendar-picker-indicator {
            filter: invert(1); /* Vuelve blanco el ícono del calendario */
            cursor: pointer;
            opacity: 0.6;
        }

        textarea:focus, input:focus {
            outline: none;
            background-color: var(--bg-input-focus);
            /* Opcional: borde sutil al enfocar */
            border-color: #444; 
        }

        textarea {
            min-height: 180px;
            resize: vertical;
            line-height: 1.5;
        }

        /* Botón Estilo Píldora (Alto Contraste) */
        button {
            width: 100%;
            background-color: var(--accent-color);
            color: #000; /* Texto negro sobre fondo blanco */
            padding: 18px;
            border: none;
            border-radius: var(--btn-radius);
            font-weight: 600;
            font-size: 1.05rem;
            cursor: pointer;
            transition: transform 0.1s ease, opacity 0.2s;
            margin-top: 10px;
        }

        button:hover {
            opacity: 0.9;
        }

        button:active {
            transform: scale(0.98); /* Efecto de click táctil */
        }

        button:disabled {
            background-color: #444;
            color: #888;
            cursor: not-allowed;
        }

        /* Helper Minimalista */
        details {
            margin-bottom: 30px;
            background: transparent;
        }

        summary {
            cursor: pointer;
            font-size: 0.9rem;
            color: var(--text-secondary);
            list-style: none;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            transition: color 0.2s;
        }
        
        summary:hover {
            color: var(--text-primary);
        }

        /* Triángulo personalizado */
        summary::before {
            content: "›";
            font-size: 1.2rem;
            line-height: 0.5;
            transition: transform 0.2s;
        }
        
        details[open] summary::before {
            transform: rotate(90deg);
        }
        
        /* Ocultar triángulo default */
        summary::-webkit-details-marker {
            display: none;
        }

        .helper-content {
            margin-top: 15px;
            padding: 20px;
            background-color: var(--bg-input);
            border-radius: 14px;
            font-size: 0.9rem;
            color: var(--text-secondary);
            line-height: 1.6;
        }

        .code-example {
            display: block;
            margin-top: 10px;
            font-family: 'SF Mono', 'Menlo', monospace;
            font-size: 0.85rem;
            color: var(--text-primary);
        }

        .sender { color: #fff; font-weight: 600; }

        .error-box {
            margin-top: 20px;
            padding: 15px;
            background-color: #3a1d1d; /* Rojo muy oscuro y desaturado */
            color: #ff8e8e;
            border-radius: 14px;
            font-size: 0.9rem;
            text-align: center;
        }
    </style>
</head>
<body>

    <div class="container">
        <h1>Generador de Rol</h1>
        <p class="subtitle">Ingresa los datos para procesar el Excel</p>

        <form method="post" action="/generar" onsubmit="startLoading()">
            
            <div class="form-group">
                <label for="texto_whatsapp">Texto de WhatsApp</label>
                <textarea name="texto_whatsapp" id="texto_whatsapp" placeholder="Pega aquí el chat..." required></textarea>
            </div>

            <div class="form-group">
                <label for="fecha_inicio">Fecha de Inicio (Semana)</label>
                <input type="date" name="fecha_inicio" id="fecha_inicio" required>
            </div>
            
            <details>
                <summary>Ver ejemplo de formato</summary>
                <div class="helper-content">
                    El sistema detectará automáticamente los patrones en el texto copiado de WhatsApp.
                    <span class="code-example">
                        [10:30] <span class="sender">Usuario:</span> Lunes 4pm. Juan. Av. Surco.<br>
                        [10:31] <span class="sender">Otro:</span> Martes 9am. Maria. Calle 1.
                    </span>
                </div>
            </details>

            <button type="submit" id="btn-submit">Generar Reporte</button>
        </form>

        {% if error %}
            <div class="error-box">
                {{ error }}
            </div>
        {% endif %}
    </div>

    <script>
        function startLoading() {
            const btn = document.getElementById('btn-submit');
            btn.textContent = 'Procesando...';
            btn.disabled = true;
        }
    </script>
</body>
</html>
"""
# --- FIN DEL FRONTEND ---

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/generar', methods=['POST'])
def generar():
    texto = request.form['texto_whatsapp']
    fecha_iso = request.form['fecha_inicio'] # Viene como YYYY-MM-DD (Estándar HTML5)

    try:
        # --- CONVERSIÓN DE FECHA ---
        # El input type="date" siempre envía YYYY-MM-DD.
        # Tu script rol_automator espera DD/MM/YYYY.
        # Hacemos la conversión aquí:
        fecha_obj = datetime.strptime(fecha_iso, "%Y-%m-%d")
        fecha_formateada = fecha_obj.strftime("%d/%m/%Y")

        # Llamamos a tu lógica original con la fecha corregida
        workbook, filename = generar_excel_desde_texto(texto, fecha_formateada, project_root)
        
        buffer = io.BytesIO()
        workbook.save(buffer)
        buffer.seek(0)

        return send_file(
            buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        return render_template_string(HTML_TEMPLATE, error=f"Error del sistema: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True, port=5001)