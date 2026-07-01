from flask import Blueprint, jsonify, request
from models import db, Product, Provider, Client, Sale, SaleDetail
from datetime import datetime

inventory_bp = Blueprint('inventory', __name__)

# OBTENER TODOS LOS PRODUCTOS
@inventory_bp.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([{
        "id": p.id,
        "name": p.name,
        "color": p.color,
        "category": p.category,
        "cost_unit": p.cost_unit,
        "stock_current": p.stock_current,
        "stock_min": p.stock_min,
        "price_retail": p.price_retail,
        "price_wholesale": p.price_wholesale,
        "location": p.location
    } for p in products])

# REGISTRAR NUEVO PRODUCTO
@inventory_bp.route('/api/products', methods=['POST'])
def add_product():
    data = request.json
    # LÓGICA DE SKU AUTOMÁTICO
    # Contamos productos actuales para generar el siguiente ID
    count = Product.query.count()
    new_sku = f"P{str(count + 1).zfill(3)}" # Genera P001, P002, etc
    new_product = Product(
        id=new_sku,
        name=data['name'],
        color=data.get('color'),
        category=data.get('category'),
        cost_unit=data['cost_unit'],
        price_retail=data['price_retail'],
        price_wholesale=data.get('price_wholesale'),
        stock_current=data['stock_current'],
        location=data.get('location'),
        stock_min=data.get('stock_min', 1)
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify({"message": "Producto creado", "id":new_sku}), 201

# ELIMINAR PRODUCTO (Opcional por ahora, pero útil)
@inventory_bp.route('/api/products/<id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get(id)
    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": "Eliminado"}), 200
    return jsonify({"message": "No encontrado"}), 404

# REGISTRAR VENTA
@inventory_bp.route('/api/sales', methods=['POST'])
def create_sale():
    data = request.json
    # 1. Buscar el producto por nombre (o ID si prefieres cambiar el input a select)
    product = Product.query.filter_by(name=data['product_name']).first()
    
    if not product:
        return jsonify({"message": "Producto no encontrado en Radarshop"}), 404
    
    if product.stock_current < data['quantity']:
        return jsonify({"message": f"Stock insuficiente. Solo quedan {product.stock_current}"}), 400

    # 2. Registrar la venta
    new_sale = Sale(
        id=f"V{datetime.now().strftime('%m%d%H%M%S')}",
        channel=data['channel'],
        payment_method=data['payment_method']
        # Aquí puedes vincular el client_id si ya existe el cliente
    )
    
    # 3. Crear el detalle y restar stock
    detail = SaleDetail(
        sale_id=new_sale.id,
        product_id=product.id,
        quantity=data['quantity'],
        price_at_sale=data['price_sold']
    )
    
    product.stock_current -= data['quantity'] # DESCUENTO AUTOMÁTICO
    
    db.session.add(new_sale)
    db.session.add(detail)
    db.session.commit()
    
    return jsonify({"message": "Venta exitosa"}), 201

# --- SECCIÓN PROVEEDORES ---
# --- LISTAR (Para que el frontend los jale) ---
@inventory_bp.route('/api/providers', methods=['GET'])
def get_providers():
    providers = Provider.query.all()
    return jsonify([{"id": p.id, "name": p.name, "phone": p.phone, "location": p.location} for p in providers])

# --- GUARDAR PROVEEDOR ---
@inventory_bp.route('/api/providers', methods=['POST'])
def add_provider():
    try:
        data = request.json
        # Generar ID automático PR001, PR002...
        count = Provider.query.count()
        new_id = f"PR{str(count + 1).zfill(3)}"
        
        new_provider = Provider(
            id=new_id,
            name=data.get('name'),
            phone=data.get('phone'),
            contact=data.get('contact'), # Si añadiste este campo
            location=data.get('location')
        )
        
        db.session.add(new_provider)
        db.session.commit() # <--- ¡ESTO ES LO QUE ASEGURA EL GUARDADO!
        
        return jsonify({"message": "Proveedor guardado", "id": new_id}), 201
    except Exception as e:
        db.session.rollback() # Si hay error, deshace cambios
        print(f"Error al guardar proveedor: {e}")
        return jsonify({"message": "Error interno", "error": str(e)}), 500

# --- LISTAR CLIENTE ---
@inventory_bp.route('/api/clients', methods=['GET'])
def get_clients():
    clients = Client.query.all()
    return jsonify([{"id": c.id, "name": c.name, "phone": c.phone, "district": c.district} for c in clients])
# --- GUARDAR CLIENTE ---
@inventory_bp.route('/api/clients', methods=['POST'])
def add_client():
    try:
        data = request.json
        count = Client.query.count()
        new_id = f"C{str(count + 1).zfill(3)}"
        
        new_client = Client(
            id=new_id,
            name=data.get('name'),
            phone=data.get('phone'),
            district=data.get('district')
        )
        
        db.session.add(new_client)
        db.session.commit()
        
        return jsonify({"message": "Cliente guardado", "id": new_id}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error al guardar cliente: {e}")
        return jsonify({"message": "Error interno", "error": str(e)}), 500
