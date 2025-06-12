from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, TelField, DateField, TimeField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length, ValidationError
from datetime import datetime, date

class CitaForm(FlaskForm):
    nombre = StringField('Nombre completo', validators=[
        DataRequired(message="El nombre es obligatorio"),
        Length(min=3, max=100, message="El nombre debe tener entre 3 y 100 caracteres")
    ])
    
    email = EmailField('Correo electrónico', validators=[
        DataRequired(message="El correo electrónico es obligatorio"),
        Email(message="Por favor, introduce una dirección de correo válida")
    ])
    
    telefono = TelField('Teléfono', validators=[
        DataRequired(message="El teléfono es obligatorio"),
        Length(min=8, max=20, message="Introduce un número de teléfono válido")
    ])
    
    fecha = DateField('Fecha preferida', validators=[
        DataRequired(message="La fecha es obligatoria")
    ], format='%Y-%m-%d')
    
    hora = TimeField('Hora preferida', validators=[
        DataRequired(message="La hora es obligatoria")
    ], format='%H:%M')
    
    tipo_consulta = SelectField('Tipo de consulta', validators=[
        DataRequired(message="Selecciona un tipo de consulta")
    ], choices=[
        ('', 'Selecciona una opción'),
        ('informacion_general', 'Información general'),
        ('prueba_vih', 'Prueba de VIH'),
        ('prueba_vph', 'Prueba de VPH'),
        ('vacuna_vph', 'Vacunación contra VPH'),
        ('consejeria', 'Consejería'),
        ('otro', 'Otro (especificar en comentarios)')
    ])
    
    comentarios = TextAreaField('Comentarios adicionales (opcional)')
    
    submit = SubmitField('Solicitar Cita')
    
    def validate_fecha(self, field):
        # Verificar que la fecha no sea en el pasado
        if field.data < date.today():
            raise ValidationError('La fecha de la cita no puede ser en el pasado')
