from blueprints import db
from flask_restful import fields

class Customers(db.Model):
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    url_foto = db.Column(db.String(200))
    password = db.Column(db.String(32), nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    sex = db.Column(db.String(10))
    address = db.Column(db.String(500))
    status = db.Column(db.Integer, default=999)

    response_fields = {
        'id': fields.Integer,
        'name': fields.String,
        'email': fields.String,
        'phone_number': fields.String,
        'sex': fields.String,
        'address': fields.String,
        'password': fields.String,
        'status': fields.String
    }

    def __init__(self, name, email, password, phone_number, address, sex, status, url_foto):
        self.name = name
        self.email = email
        self.password = password
        self.address = address
        self.sex = sex
        self.phone_number = phone_number
        self.status = status
        self.url_foto = url_foto

    def __repr__(self):
        return '<Customer %r>' % self.id

# if multiple address needed
# class CustomerAddress(db.Model):
#     __tablename__ = "customeraddress"

#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     address = db.Column(db.Text)
#     city = db.Column(db.String(50), nullable=False)
#     province = db.Column(db.String(30), nullable=False)
#     postcode = db.Column(db.Integer(5), nullable=False)
#     id = db.Column(db.Integer, db.ForeignKey(customers.id), nullable=False)

#     response_fields = {
#         'address': fields.String,
#         'city': fields.String,
#         'province': fields.String,
#         'postcode': fields.Integer
#     }

#     def __init__(self, id, postcode, province, city, address):
#         self.address = address
#         self.city = city
#         self.province = province
#         self.postcode = postcode
#         self.id = id

#     def __repr__(self):
#         return '<CustomerAddress %r>' % self.id
