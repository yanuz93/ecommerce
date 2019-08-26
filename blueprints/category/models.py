from blueprints import db
from flask_restful import fields

class Category(db.Model):
    __tablename__ = "category"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_name = db.Column(db.String(50), nullable=False)

    response_fields = {
        'id': fields.Integer,
        'category_name': fields.String,
    }

    def __init__(self, category_name):
        self.category_name = category_name

    def __repr__(self):
        return '<Category %r>' % self.id
