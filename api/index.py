# api/index.py

from flask import Flask, request, render_template_string, send_file
import io
import os
import sys

# --- INICIO: Lógica para resolver importaciones ---
# Esto es necesario para que Python encuentre los módulos en la carpeta raíz del proyecto
# cuando se ejecuta desde la subcarpeta 'api'.
base_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(base_dir, '..')
sys.path.insert(0, project_root)
from rol_automator import generar_excel_desde_texto
# --- FIN: Lógica para resolver importaciones ---

# Inicializar la aplicación Flask
app = Flask(__name__)


# --- INICIO DEL FRONTEND ---
# Plantilla HTML para el formulario (se puede mover a un archivo .html separado)
HTML_TEMPLATE = """
<!doctype html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Generador de Rol</title>
    <style>
        body { font-family: sans-serif; max-width: 800px; margin: auto; padding: 1em; background-color: #f4f4f9; }
        textarea { width: 100%; height: 200px; margin-bottom: 1em; }
        input[type=text] { width: 100%; padding: 8px; margin-bottom: 1em; }
        input[type=submit] { background-color: #007bff; color: white; padding: 10px 20px; border: none; cursor: pointer; }
        .error { color: red; }
    </style>
</head>
<body>
    <h1>Generador de Rol de Predicación</h1>
    <p>Pega el texto de WhatsApp y la fecha de inicio de la semana.</p>
    <form method="post" action="/generar">
        <label for="texto_whatsapp">Texto de WhatsApp:</label><br>
        <textarea name="texto_whatsapp" id="texto_whatsapp" required></textarea><br>
        
        <label for="fecha_inicio">Fecha de Inicio (DD/MM/AAAA):</label><br>
        <input type="text" name="fecha_inicio" id="fecha_inicio" required placeholder="Ej: 27/10/2025"><br>
        
        <input type="submit" value="Generar Excel">
    </form>
    {% if error %}
        <p class="error"><strong>Error:</strong> {{ error }}</p>
    {% endif %}
</body>
</html>
"""
# --- FIN DEL FRONTEND ---

@app.route('/')
def index():
    """Muestra la página principal con el formulario."""
    return render_template_string(HTML_TEMPLATE)

@app.route('/generar', methods=['POST'])
def generar():
    """Procesa los datos del formulario y devuelve el archivo Excel."""
    texto = request.form['texto_whatsapp']
    fecha = request.form['fecha_inicio']

    try:
        # Llama a la función principal de tu script, pasando la ruta raíz del proyecto
        workbook, filename = generar_excel_desde_texto(texto, fecha, project_root)

        # Guarda el libro de trabajo en un buffer de memoria en lugar de un archivo físico
        buffer = io.BytesIO()
        workbook.save(buffer)
        buffer.seek(0)

        # Envía el buffer como un archivo para descargar
        return send_file(
            buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        # Si algo sale mal, vuelve a mostrar el formulario con un mensaje de error
        return render_template_string(HTML_TEMPLATE, error=str(e))

# El siguiente bloque solo se ejecuta cuando corres el script directamente
# y es ignorado por Vercel.
if __name__ == '__main__':
    app.run(debug=True, port=5001)