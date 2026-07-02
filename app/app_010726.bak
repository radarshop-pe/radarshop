from flask import Flask, send_from_directory
from flask_cors import CORS
from models import db
from routes import inventory_bp

app = Flask(__name__, static_folder='static')
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///radarshop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.register_blueprint(inventory_bp)

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        from models import Category
        defaults = ['Hogar', 'Cocina', 'Oficina', 'Accesorios mujer', 'Electronica', 'Limpieza', 'Otros']
        for name in defaults:
            if not Category.query.filter_by(name=name).first():
                db.session.add(Category(name=name))
        db.session.commit()
        print('\n  Radarshop corriendo en http://localhost:5000\n')
    # host='0.0.0.0' le dice a Flask que acepte conexiones de cualquier dispositivo en la red
    app.run(debug=True, host='0.0.0.0', port=5000)
