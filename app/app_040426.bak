from flask import Flask, send_from_directory
from models import db
from routes import inventory_bp # Asumiendo que usas Blueprints o importas tus rutas

app = Flask(__name__, static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///radarshop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Registro de tus rutas (donde está la lógica de Excel y APIs)
app.register_blueprint(inventory_bp) 

# Ruta para servir el panel visual
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Crea la base de datos si no existe
    app.run(debug=True, port=5000)