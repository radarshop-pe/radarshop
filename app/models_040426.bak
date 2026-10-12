from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# TABLA DE PROVEEDORES (Debe estar antes o definida para que Product la vea)
class Provider(db.Model):
    id = db.Column(db.String(10), primary_key=True) # PR001
    name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    location = db.Column(db.String(200))
    products = db.relationship('Product', backref='provider', lazy=True)

# TABLA DE CLIENTES
class Client(db.Model):
    id = db.Column(db.String(10), primary_key=True) # C001
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    district = db.Column(db.String(100))
    sales = db.relationship('Sale', backref='client', lazy=True)

class Product(db.Model):
    id = db.Column(db.String(10), primary_key=True) # P001
    name = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(50))
    category = db.Column(db.String(50))
    cost_unit = db.Column(db.Float, nullable=False)
    price_retail = db.Column(db.Float, nullable=False)
    price_wholesale = db.Column(db.Float)
    stock_current = db.Column(db.Integer, default=0)
    stock_min = db.Column(db.Integer, default=1)
    location = db.Column(db.String(50)) # Ej: Estante A1
    provider_id = db.Column(db.String(10), db.ForeignKey('provider.id'))

class Sale(db.Model):
    id = db.Column(db.String(10), primary_key=True) # V001
    date = db.Column(db.DateTime, default=datetime.utcnow)
    client_id = db.Column(db.String(10), db.ForeignKey('client.id'))
    channel = db.Column(db.String(50)) # Facebook, Whatsapp
    payment_method = db.Column(db.String(50)) # Yape, Plin, Efectivo
    delivery_cost = db.Column(db.Float, default=0.0)
    
    # Propiedad calculada para el total (No se guarda en BD, se genera al consultar)
    @property
    def total_income(self):
        return sum(detail.quantity * detail.price_at_sale for detail in self.details) + self.delivery_cost

class SaleDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.String(10), db.ForeignKey('sale.id'))
    product_id = db.Column(db.String(10), db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer, nullable=False)
    price_at_sale = db.Column(db.Float) # Guardamos el precio del momento