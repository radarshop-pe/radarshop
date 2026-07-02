from flask import Flask, send_from_directory, session, jsonify, request
from flask_cors import CORS
from models import db
from routes import inventory_bp
import os

app = Flask(__name__, static_folder='static')
CORS(app, supports_credentials=True)

# ── CONFIGURACIÓN ─────────────────────────────────────────
db_url = os.environ.get('DATABASE_URL', 'sqlite:///radarshop.db')
# Supabase a veces retorna 'postgres://' — SQLAlchemy necesita 'postgresql://'
if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'local-dev-key-cambiar-en-produccion')

db.init_app(app)
app.register_blueprint(inventory_bp)

# ── INICIALIZAR BD ────────────────────────────────────────
with app.app_context():
    db.create_all()
    from models import Category
    defaults = ['Hogar', 'Cocina', 'Oficina', 'Accesorios mujer',
                'Electronica', 'Limpieza', 'Belleza', 'Otros']
    for name in defaults:
        if not Category.query.filter_by(name=name).first():
            db.session.add(Category(name=name))
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()

# ── AUTH HELPERS ──────────────────────────────────────────
def get_users():
    """Lee usuarios desde variables de entorno de Vercel."""
    users = {}
    for i in range(1, 6):
        email = os.environ.get(f'USER_{i}_EMAIL', '').strip().lower()
        pwd   = os.environ.get(f'USER_{i}_PASSWORD', '').strip()
        if email and pwd:
            users[email] = pwd
    return users

# ── RUTAS DE AUTENTICACIÓN ────────────────────────────────
@app.route('/login', methods=['POST'])
def login():
    data     = request.json or {}
    email    = (data.get('email') or '').strip().lower()
    password = (data.get('password') or '').strip()
    users    = get_users()
    if email in users and users[email] == password:
        session.permanent = True
        session['user']   = email
        return jsonify({'ok': True, 'user': email})
    return jsonify({'ok': False, 'message': 'Correo o contraseña incorrectos'}), 401

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'ok': True})

@app.route('/api/me', methods=['GET'])
def me():
    if 'user' in session:
        return jsonify({'ok': True, 'user': session['user']})
    return jsonify({'ok': False, 'message': 'No autenticado'}), 401

# ── SERVIR FRONTEND ───────────────────────────────────────
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_files(path):
    try:
        return send_from_directory(app.static_folder, path)
    except Exception:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)