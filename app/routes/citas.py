from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
import os
import json
from datetime import datetime, timedelta
import google.auth.transport.requests
import google.oauth2.credentials
import googleapiclient.discovery
from google_auth_oauthlib.flow import Flow
from app import db
from app.models.cita import Cita
from app.forms.cita_form import CitaForm

citas_bp = Blueprint('citas', __name__, url_prefix='/citas')

# Configuración de Google OAuth
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Solo para desarrollo local

def create_google_flow():
    """Crea y configura el flujo de autenticación de Google OAuth"""
    from flask import current_app
    
    try:
        client_config = {
            "web": {
                "client_id": current_app.config.get('GOOGLE_CLIENT_ID'),
                "client_secret": current_app.config.get('GOOGLE_CLIENT_SECRET'),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [current_app.config.get('GOOGLE_REDIRECT_URI')]
            }
        }

        # Definir scopes consistentes que incluyan OpenID
        scopes = [
            'https://www.googleapis.com/auth/calendar.events',
            'https://www.googleapis.com/auth/userinfo.email',
            'openid'
        ]

        flow = Flow.from_client_config(
            client_config,
            scopes=scopes
        )
        flow.redirect_uri = current_app.config.get('GOOGLE_REDIRECT_URI')
        return flow
    except Exception as e:
        print(f"Error al crear Google Flow: {str(e)}")
        raise

def create_calendar_event(credentials, cita_data):
    """Crea un evento en Google Calendar con integración a Google Meet"""
    try:
        service = googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)

        # Combinar fecha y hora
        fecha_hora_str = f"{cita_data['fecha']} {cita_data['hora']}"
        fecha_inicio = datetime.strptime(fecha_hora_str, '%Y-%m-%d %H:%M')
        fecha_fin = fecha_inicio + timedelta(hours=1)

        # Mapeo de tipos de consulta
        tipos_consulta = {
            'informacion_general': 'Consulta de información general',
            'prueba_vih': 'Prueba de VIH',
            'prueba_vph': 'Prueba de VPH',
            'vacuna_vph': 'Vacunación contra VPH',
            'consejeria': 'Sesión de consejería',
            'otro': 'Consulta especializada'
        }

        descripcion_consulta = tipos_consulta.get(cita_data['tipo_consulta'], 'Consulta médica')

        # Crear el evento con integración Google Meet
        evento = {
            'summary': f'Cita médica - {descripcion_consulta}',
            'description': f"""
Cita médica programada:
- Tipo: {descripcion_consulta}
- Paciente: {cita_data['nombre']}
- Centro de Salud Sexual
- Teléfono: (123) 456-7890

{cita_data.get('comentarios', '')}

IMPORTANTE: Confirme su asistencia llamando al centro 24 horas antes.
            """.strip(),
            'start': {
                'dateTime': fecha_inicio.isoformat(),
                'timeZone': 'Centro/Tarija',
            },
            'end': {
                'dateTime': fecha_fin.isoformat(),
                'timeZone': 'Centro/Tarija',
            },
            'location': 'Cies, Calle Bolivar # 475 entre Santa Cruz y Mendez,Tarija ',
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},  # 24 horas antes
                    {'method': 'popup', 'minutes': 60},       # 1 hora antes
                ],
            },
            'attendees': [
                {'email': cita_data['email']}
            ],
            'conferenceData': {
                'createRequest': {
                    'requestId': f"meet-{datetime.now().timestamp()}",
                    'conferenceSolutionKey': {
                        'type': 'hangoutsMeet'
                    }
                }
            }
        }

        # Insertar evento con soporte para Google Meet
        evento_creado = service.events().insert(
            calendarId='primary',
            body=evento,
            conferenceDataVersion=1
        ).execute()

        return evento_creado

    except Exception as e:
        print(f"Error al crear evento en Google Calendar: {str(e)}")
        return None

def crear_cita_desde_datos(cita_data):
    """Crea un objeto Cita con los tipos de datos correctos"""
    try:
        # Convertir fecha string a objeto date
        fecha_obj = datetime.strptime(cita_data['fecha'], '%Y-%m-%d').date()
        
        # Convertir hora string a objeto time
        hora_obj = datetime.strptime(cita_data['hora'], '%H:%M').time()
        
        # Crear la cita con los tipos correctos
        cita = Cita(
            nombre=cita_data['nombre'],
            email=cita_data['email'],
            telefono=cita_data['telefono'],
            fecha=fecha_obj,
            hora=hora_obj,
            tipo_consulta=cita_data['tipo_consulta'],
            comentarios=cita_data.get('comentarios', '')
        )
        
        return cita
    except ValueError as e:
        raise ValueError(f"Error en formato de fecha u hora: {str(e)}")
    except Exception as e:
        raise Exception(f"Error al crear la cita: {str(e)}")

def validar_datos_cita(cita_data):
    """Valida los datos de la cita"""
    campos_requeridos = ['nombre', 'email', 'telefono', 'fecha', 'hora', 'tipo_consulta']
    
    # Verificar campos obligatorios
    for campo in campos_requeridos:
        if not cita_data.get(campo):
            return False, f'El campo {campo} es obligatorio.'
    
    # Validar formato de fecha
    try:
        fecha_cita = datetime.strptime(cita_data['fecha'], '%Y-%m-%d').date()
        if fecha_cita < datetime.now().date():
            return False, 'No puedes agendar una cita en el pasado.'
    except ValueError:
        return False, 'Formato de fecha inválido.'
    
    # Validar formato de hora
    try:
        datetime.strptime(cita_data['hora'], '%H:%M')
    except ValueError:
        return False, 'Formato de hora inválido.'
    
    return True, 'Datos válidos'

@citas_bp.route('/', methods=['GET', 'POST'])
def agendar():
    """Ruta principal para agendar citas"""
    form = CitaForm()
    
    if request.method == 'POST':
        # Recopilar datos del formulario
        cita_data = {
            'nombre': request.form.get('nombre', '').strip(),
            'email': request.form.get('email', '').strip(),
            'telefono': request.form.get('telefono', '').strip(),
            'fecha': request.form.get('fecha', '').strip(),
            'hora': request.form.get('hora', '').strip(),
            'tipo_consulta': request.form.get('tipo_consulta', '').strip(),
            'comentarios': request.form.get('comentarios', '').strip()
        }

        # Validar datos
        es_valido, mensaje = validar_datos_cita(cita_data)
        if not es_valido:
            flash(mensaje, 'error')
            return render_template('citas/form.html', titulo='Agendar Cita', form=form, form_data=cita_data)

        # Guardar datos en sesión
        session['cita_pendiente'] = cita_data

        # Verificar si se quiere sincronizar con Google Calendar
        sincronizar_calendar = request.form.get('sincronizar_google') == 'on'

        if sincronizar_calendar:
            try:
                flow = create_google_flow()
                authorization_url, state = flow.authorization_url(
                    access_type='offline',
                    include_granted_scopes='true'
                )
                session['state'] = state
                return redirect(authorization_url)
            except Exception as e:
                flash(f'Error al conectar con Google Calendar: {str(e)}', 'error')
                # Continuar sin sincronización
                pass
        
        # Guardar cita sin sincronización con Google Calendar
        try:
            cita = crear_cita_desde_datos(cita_data)
            db.session.add(cita)
            db.session.commit()
            flash('Tu cita ha sido agendada correctamente. Te contactaremos para confirmar.', 'success')
            session.pop('cita_pendiente', None)
            return redirect(url_for('citas.agendar'))
        except Exception as e:
            flash(f'Error al guardar la cita: {str(e)}', 'error')
            db.session.rollback()

    return render_template('citas/form.html', titulo='Agendar Cita', form=form)

@citas_bp.route('/google_callback')
def google_callback():
    """Callback para manejar la respuesta de Google OAuth"""
    try:
        # Crear un nuevo flow para el callback (esto es importante)
        flow = create_google_flow()
        
        # Obtener el token usando la URL de autorización completa
        flow.fetch_token(authorization_response=request.url)

        credentials = flow.credentials
        cita_data = session.get('cita_pendiente')

        if not cita_data:
            flash('Error: No se encontraron datos de la cita.', 'error')
            return redirect(url_for('citas.agendar'))

        # Crear evento en Google Calendar
        evento = create_calendar_event(credentials, cita_data)

        # Guardar cita en la base de datos
        try:
            cita = crear_cita_desde_datos(cita_data)
            db.session.add(cita)
            db.session.commit()

            if evento:
                flash('Tu cita ha sido agendada y añadida a tu Google Calendar.', 'success')
            else:
                flash('Tu cita fue agendada, pero no se pudo sincronizar con Google Calendar.', 'warning')

        except Exception as e:
            flash(f'Error al guardar la cita: {str(e)}', 'error')
            db.session.rollback()

        # Limpiar sesión
        session.pop('cita_pendiente', None)
        session.pop('state', None)

        return redirect(url_for('citas.agendar'))

    except Exception as e:
        flash(f'Error durante la autenticación con Google: {str(e)}', 'error')
        session.pop('cita_pendiente', None)
        session.pop('state', None)
        return redirect(url_for('citas.agendar'))

@citas_bp.route('/lista')
def lista():
    """Lista todas las citas (para personal médico)"""
    try:
        citas = Cita.query.order_by(Cita.fecha, Cita.hora).all()
        return render_template('citas/lista.html', titulo='Lista de Citas', citas=citas)
    except Exception as e:
        flash(f'Error al cargar las citas: {str(e)}', 'error')
        return render_template('citas/lista.html', titulo='Lista de Citas', citas=[])

@citas_bp.route('/<int:id>')
def detalle(id):
    """Muestra el detalle de una cita específica"""
    try:
        cita = Cita.query.get_or_404(id)
        return render_template('citas/detalle.html', titulo='Detalle de Cita', cita=cita)
    except Exception as e:
        flash(f'Error al cargar la cita: {str(e)}', 'error')
        return redirect(url_for('citas.lista'))

@citas_bp.route('/<int:id>/cambiar-estado/<estado>')
def cambiar_estado(id, estado):
    """Cambia el estado de una cita"""
    estados_validos = ['pendiente', 'confirmada', 'cancelada', 'completada']
    
    if estado not in estados_validos:
        flash('Estado no válido.', 'error')
        return redirect(url_for('citas.lista'))
    
    try:
        cita = Cita.query.get_or_404(id)
        cita.estado = estado
        db.session.commit()
        
        flash(f'El estado de la cita ha sido actualizado a: {estado}', 'success')
    except Exception as e:
        flash(f'Error al actualizar el estado: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('citas.lista'))

@citas_bp.route('/test-calendar')
def test_calendar():
    """Ruta para probar la configuración de Google Calendar"""
    from flask import current_app
    
    config_status = {
        'GOOGLE_CLIENT_ID': bool(current_app.config.get('GOOGLE_CLIENT_ID')),
        'GOOGLE_CLIENT_SECRET': bool(current_app.config.get('GOOGLE_CLIENT_SECRET')),
        'GOOGLE_REDIRECT_URI': current_app.config.get('GOOGLE_REDIRECT_URI'),
        'GOOGLE_SCOPES': current_app.config.get('GOOGLE_SCOPES', [])
    }
    
    return jsonify(config_status)