from flask import Blueprint, render_template

recursos_bp = Blueprint('recursos', __name__, url_prefix='/recursos')

@recursos_bp.route('/')
def index():
    recursos = [
        {
            'titulo': 'Guía de prevención del VIH',
            'descripcion': 'Información detallada sobre métodos de prevención del VIH.',
            'enlace': '#'
        },
        {
            'titulo': 'Tratamientos actuales para el SIDA',
            'descripcion': 'Avances médicos y tratamientos disponibles.',
            'enlace': '#'
        },
        {
            'titulo': 'Vacunas contra el VPH',
            'descripcion': 'Información sobre las vacunas disponibles contra el Virus del Papiloma Humano.',
            'enlace': '#'
        }
    ]
    return render_template('recursos.html', titulo='Recursos', recursos=recursos)
