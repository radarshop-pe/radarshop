from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(200))
    products = db.relationship('Product', backref='category_obj', lazy=True)

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'description': self.description}


class Provider(db.Model):
    __tablename__ = 'provider'
    id = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    location = db.Column(db.String(200))
    type = db.Column(db.String(50), default='Importador')
    quality = db.Column(db.Integer, default=3)
    notes = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    products = db.relationship('Product', backref='provider', lazy=True)

    def to_dict(self):
        return {
            'id': self.id, 'name': self.name, 'contact': self.contact,
            'phone': self.phone, 'location': self.location,
            'type': self.type, 'quality': self.quality, 'notes': self.notes
        }


class Client(db.Model):
    __tablename__ = 'client'
    id = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    district = db.Column(db.String(100))
    status = db.Column(db.String(20), default='Activo')
    notes = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sales = db.relationship('Sale', backref='client', lazy=True)

    @property
    def total_spent(self):
        total = 0
        for sale in self.sales:
            total += sale.total_income
        return round(total, 2)

    @property
    def total_orders(self):
        return len(self.sales)

    def to_dict(self):
        return {
            'id': self.id, 'name': self.name, 'phone': self.phone,
            'district': self.district, 'status': self.status, 'notes': self.notes,
            'total_spent': self.total_spent, 'total_orders': self.total_orders,
            'created_at': self.created_at.strftime('%d/%m/%Y') if self.created_at else ''
        }


class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(50))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    cost_unit = db.Column(db.Float, nullable=False, default=0)
    price_retail = db.Column(db.Float, nullable=False, default=0)
    price_wholesale = db.Column(db.Float, default=0)
    stock_current = db.Column(db.Integer, default=0)
    stock_min = db.Column(db.Integer, default=1)
    location = db.Column(db.String(50))
    provider_id = db.Column(db.String(10), db.ForeignKey('provider.id'))
    status = db.Column(db.String(20), default='Activo')
    notes = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sale_details = db.relationship('SaleDetail', backref='product', lazy=True)

    @property
    def margin_pct(self):
        if self.price_retail and self.price_retail > 0:
            return round((self.price_retail - self.cost_unit) / self.price_retail * 100, 1)
        return 0

    @property
    def stock_alert(self):
        return self.stock_current <= self.stock_min

    def to_dict(self):
        return {
            'id': self.id, 'name': self.name, 'color': self.color,
            'category_id': self.category_id,
            'category': self.category_obj.name if self.category_obj else '',
            'cost_unit': self.cost_unit, 'price_retail': self.price_retail,
            'price_wholesale': self.price_wholesale,
            'stock_current': self.stock_current, 'stock_min': self.stock_min,
            'location': self.location,
            'provider_id': self.provider_id,
            'provider': self.provider.name if self.provider else '',
            'margin_pct': self.margin_pct,
            'stock_alert': self.stock_alert,
            'status': self.status, 'notes': self.notes
        }


class Sale(db.Model):
    __tablename__ = 'sale'
    id = db.Column(db.String(15), primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    client_id = db.Column(db.String(10), db.ForeignKey('client.id'))
    channel = db.Column(db.String(50))
    payment_method = db.Column(db.String(50))
    delivery_cost = db.Column(db.Float, default=0.0)
    delivery_type = db.Column(db.String(50), default='Delivery')
    status = db.Column(db.String(20), default='Completado')
    notes = db.Column(db.String(300))
    details = db.relationship('SaleDetail', backref='sale', lazy=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('seller.id'), nullable=True) # Cambio a ForeignKey
    seller = db.relationship('Seller', backref='sales', lazy=True) # Relación para jalar el nombre fácil

    @property
    def total_income(self):
        return round(sum(d.quantity * d.price_at_sale for d in self.details) + self.delivery_cost, 2)

    @property
    def total_cost(self):
        return round(sum(d.quantity * d.cost_at_sale for d in self.details), 2)

    @property
    def total_profit(self):
        return round(self.total_income - self.total_cost - self.delivery_cost, 2)

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.strftime('%d/%m/%Y %H:%M') if self.date else '',
            'client_id': self.client_id,
            'client_name': self.client.name if self.client else 'Sin cliente',
            'seller_name': self.seller.name if self.seller else 'Sin vendedor',
            'channel': self.channel,
            'payment_method': self.payment_method,
            'delivery_cost': self.delivery_cost,
            'delivery_type': self.delivery_type,
            'status': self.status,
            'total_income': self.total_income,
            'total_cost': self.total_cost,
            'total_profit': self.total_profit,
            'details': [d.to_dict() for d in self.details]
        }


class SaleDetail(db.Model):
    __tablename__ = 'sale_detail'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sale_id = db.Column(db.String(15), db.ForeignKey('sale.id'))
    product_id = db.Column(db.String(10), db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price_at_sale = db.Column(db.Float, default=0)
    cost_at_sale = db.Column(db.Float, default=0)

    def to_dict(self):
        return {
            'id': self.id, 'product_id': self.product_id,
            'product_name': self.product.name if self.product else '',
            'quantity': self.quantity,
            'price_at_sale': self.price_at_sale,
            'cost_at_sale': self.cost_at_sale,
            'subtotal': round(self.quantity * self.price_at_sale, 2)
        }


class Inquiry(db.Model):
    __tablename__ = 'inquiry'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    product_id = db.Column(db.String(10), db.ForeignKey('product.id'), nullable=True)
    product_name = db.Column(db.String(100))
    client_name = db.Column(db.String(100))
    channel = db.Column(db.String(50))
    question = db.Column(db.String(300))
    result = db.Column(db.String(30), default='Pendiente')
    no_buy_reason = db.Column(db.String(200))

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.strftime('%d/%m/%Y') if self.date else '',
            'product_id': self.product_id,
            'product_name': self.product_name,
            'client_name': self.client_name,
            'channel': self.channel,
            'question': self.question,
            'result': self.result,
            'no_buy_reason': self.no_buy_reason
        }
    
class Seller(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    status = db.Column(db.String(20), default='Activo') # Activo/Inactivo
    notes = db.Column(db.String(300))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone or '',
            'status': self.status,
            'notes': self.notes or ''
        }