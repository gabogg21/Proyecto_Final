import sys
from flask import Flask
from app import create_app, db
from app.models.cita import Cita
from app.models.usuario import Usuario
import os
from dotenv import load_dotenv
load_dotenv()  # Cargar variables del archivo .env

app = create_app()

@app.shell_context_processor
def make_shell_context():
    """Provide additional context for the Flask shell."""
    return {
        'db': db,
        'Cita': Cita,
        'Usuario': Usuario,
        # Add more models here as your application grows
    }

if __name__ == '__main__':
    # Configure the port and host for the development environment
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

# def resource_path(relative_path):
#     """Permite encontrar recursos al empaquetar con PyInstaller."""
#     base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
#     return os.path.join(base_path, relative_path)

# app = Flask(
#     __name__,
#     template_folder=resource_path("app/templates"),
#     static_folder=resource_path("app/static")
# )