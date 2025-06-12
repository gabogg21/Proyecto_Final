from flask import Blueprint, render_template

recomendaciones_bp = Blueprint('recomendaciones', __name__, url_prefix='/recomendaciones')

@recomendaciones_bp.route('/')
def index():
    recomendaciones = {
        'vih_sida': [
            'Usa protección en todas las relaciones sexuales',
            'Hazte pruebas de detección regularmente',
            'Conoce el estado de VIH de tu pareja',
            'No compartas jeringas u otros objetos punzantes',
            'Infórmate sobre la PrEP (Profilaxis Pre-Exposición)'
        ],
        'vph': [
            'Vacúnate contra el VPH según las recomendaciones médicas',
            'Realiza chequeos ginecológicos/urológicos regulares',
            'Usa protección en relaciones sexuales',
            'Limita el número de parejas sexuales',
            'Hazte la prueba de Papanicolaou (mujeres) regularmente'
        ]
    }
    return render_template('recomendaciones.html', titulo='Recomendaciones', recomendaciones=recomendaciones)
