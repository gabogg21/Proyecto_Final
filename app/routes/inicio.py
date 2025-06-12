# app/routes/inicio.py - Rutas para la página de inicio
from flask import Blueprint, render_template, current_app

inicio_bp = Blueprint('inicio', __name__)

@inicio_bp.route('/')
@inicio_bp.route('/inicio')
def index():
    # Imprime información de depuración
    print("Intentando renderizar la página de inicio")
    print(f"Template folder: {current_app.template_folder}")
    try:
        return render_template('inicio.html', titulo='Inicio - Información sobre VIH, SIDA y VPH')
    except Exception as e:
        print(f"Error al renderizar la plantilla: {e}")
        # Devuelve un texto simple en caso de error con la plantilla
        return "Error al cargar la página de inicio. Verifica las plantillas. Error: " + str(e)