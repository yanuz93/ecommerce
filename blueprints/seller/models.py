from blueprints import db
from flask_restful import fields
# from blueprints.customer.models import Customer

class Sellers(db.Model):
    __tablename__ = "sellers"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    address = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(50))
    province = db.Column(db.String(30))
    postcode = db.Column(db.Integer)
    status = db.Column(db.Integer)
    url_foto = db.Column(db.String(200))

    response_fields = {
        'id': fields.Integer,
        'name': fields.String,
        'email': fields.String,
        'password': fields.String,
        'phone_number': fields.String,
        'address': fields.String,
        'city': fields.String,
        'province': fields.String,
        'postcode': fields.Integer,
        'status': fields.Integer,
        'url_foto': fields.String
    }

    def __init__(self, name, email, password, phone_number, address, city, province, postcode, status, url_foto):
        self.name = name
        self.email = email
        self.password = password
        self.phone_number = phone_number
        self.address = address
        self.city = city
        self.province = province
        self.postcode = postcode
        self.url_foto = url_foto
        self.status = status

    def __repr__(self):
        return '<Sellers %r>' % self.id
