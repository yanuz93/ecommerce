from blueprints import db
from flask_restful import fields

class Products(db.Model):
    __tablename__ = "product"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Integer, nullable=False)
    url_foto = db.Column(db.String(200))
    discount = db.Column(db.Integer)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('sellers.id'), nullable=False)

    response_fields = {
        'id': fields.Integer,
        'name': fields.String,
        'description': fields.String,
        'category_id': fields.Integer,
        'stock': fields.Integer,
        'unit_price': fields.Integer,
        'seller_id': fields.Integer,
        'discount': fields.Integer,
        'url_foto': fields.String
    }

    def __init__(self, name, description, category_id, stock, unit_price, discount, seller_id, url_foto):
        self.name = name
        self.category_id = category_id
        self.stock = stock
        self.unit_price = unit_price
        self.seller_id = seller_id
        self.url_foto = url_foto
        self.description = description
        self.discount = discount

    def __repr__(self):
        return '<Product %r>' % self.id
