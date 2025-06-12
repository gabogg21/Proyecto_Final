from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Información sobre VIH, SIDA y VPH</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/css/bootstrap.min.css">
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
            <div class="container">
                <a class="navbar-brand" href="#">Salud Sexual</a>
                <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                    <span class="navbar-toggler-icon"></span>
                </button>
                <div class="collapse navbar-collapse" id="navbarNav">
                    <ul class="navbar-nav ms-auto">
                        <li class="nav-item">
                            <a class="nav-link active" href="#">Inicio</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/recursos">Recursos</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/recomendaciones">Recomendaciones</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/citas">Agendar Cita</a>
                        </li>
                    </ul>
                </div>
            </div>
        </nav>

        <div class="container mt-4">
            <div class="jumbotron p-4 bg-light rounded-3">
                <h1 class="display-4">Información sobre VIH, SIDA y VPH</h1>
                <p class="lead">Portal informativo para la prevención, detección y tratamiento del VIH, SIDA y el Virus del Papiloma Humano.</p>
                <hr class="my-4">
                <p>La información correcta es fundamental para prevenir estas infecciones y mantener una buena salud sexual.</p>
            </div>
        </div>

        <script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """

@app.route('/recursos')
def recursos():
    return "<h1>Página de Recursos</h1><p>Esta es una página de prueba.</p>"

@app.route('/recomendaciones')
def recomendaciones():
    return "<h1>Página de Recomendaciones</h1><p>Esta es una página de prueba.</p>"

@app.route('/citas')
def citas():
    return "<h1>Agendar Cita</h1><p>Esta es una página de prueba.</p>"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)