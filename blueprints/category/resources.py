from flask import Blueprint
from flask_restful import Resource, Api, reqparse, marshal, inputs
from .models import Category
from sqlalchemy import desc
from blueprints import app, db, admin_required
from flask_jwt_extended import jwt_required, get_jwt_claims, jwt_required

bp_category = Blueprint('category', __name__)
api = Api(bp_category)

class CategoryResource(Resource):
    def __init__(self):
        pass
    def options(self, id=None):
        return {"status": "oke"}    
    def get(self, id):
        qry = Category.query.get(id)
        if qry is not None:
            return marshal(qry, Category.response_fields), 200, {'Content-Type': 'application/json'}
        return {'status': 'Category Not Found'}, 404, {'Content-Type': 'application/json'}

    @jwt_required
    @admin_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('category', location='json', required=True)
        data = parser.parse_args()

        kategori = Category(data['category'])
        db.session.add(kategori)
        db.session.commit()

        app.logger.debug('DEBUG : %s', kategori)

        return marshal(kategori, Category.response_fields), 200, {'Content-Type': 'application/json'}

    @jwt_required
    @admin_required
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('category', location='json', required=True)
        args = parser.parse_args()
        
        qry = Category.query.get()
        qry.category = args['category']
        db.session.commit()

        return marshal(qry, Category.response_fields), 200, {'Content-Type': 'application/json'}

    @jwt_required
    @admin_required
    def delete(self, id):
        qry = Category.query.get(id)
        if qry is None:
            return {'status': 'Category Not Found'}, 404, {'Content-Type': 'application/json'}

        db.session.delete(qry)
        db.session.commit()

        return {'status': 'Category Deleted'}, 200, {'Content-Type': 'application/json'}

    def patch(self):
        return 'Not yet implemented', 501

class CategoryList(Resource):

    def __init__(self):
        pass

    @jwt_required
    @admin_required
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('p', type=int, location='args', default=1)
        parser.add_argument('rp', type=int, location='args', default=25)
        args = parser.parse_args()

        offset = (args['p'] * args['rp']) - args['rp']

        qry = Category.query

        rows = []
        for row in qry.limit(args['rp']).offset(offset).all():
            rows.append(marshal(row, Category.response_fields))
        return rows, 200, {'Content-Type': 'application/json'}

api.add_resource(CategoryList, '')
api.add_resource(CategoryResource, '', '/<id>')

