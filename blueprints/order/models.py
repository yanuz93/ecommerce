from blueprints import db
from flask_restful import fields

class Orders(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    total_qty = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Boolean, default= False)
    createdAt = db.Column(db.DateTime, default= db.func.current_timestamp())
    updatedAt = db.Column(db.DateTime, default= db.func.current_timestamp())
    
    response_fields = {
        'id': fields.Integer,
        'total_qty': fields.Integer,
        'total_price': fields.Integer,
        "updatedAt": fields.String
    }

    def __init__(self, customer_id, total_qty, total_price, status):
        self.customer_id = customer_id
        self.total_qty = total_qty
        self.total_price = total_price
        self.status = status

    def __repr__(self):
        return '<Orders %r>' % self.id

class OrderDetails(db.Model):
    __tablename__ = "orderdetails"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    qty = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Integer)
    createdAt = db.Column(db.DateTime, default= db.func.current_timestamp())
    updatedAt = db.Column(db.DateTime, default= db.func.current_timestamp())

    response_fields = {
        'id': fields.Integer,
        'product_id': fields.Integer,
        'qty': fields.Integer,
        'price': fields.Integer,
        'product_name': fields.String,
        'seller_name': fields.String
    }

    def __init__(self, order_id, product_id, qty, price, status, updatedAt):
        self.order_id = order_id
        self.product_id = product_id
        self.qty = qty
        self.price = price
        self.status = status
        self.updatedAt = updatedAt

    def __repr__(self):
        return '<OrderDetails %r>' % self.id