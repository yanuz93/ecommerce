from flask import Blueprint
from flask_restful import Resource, Api, reqparse, marshal, inputs
from .models import Products
from sqlalchemy import desc
from blueprints import app, db, seller_required
from flask_jwt_extended import jwt_required, get_jwt_claims, get_jwt_identity

bp_product = Blueprint('products', __name__)
api = Api(bp_product)

class ProductResource(Resource):

    def __init__(self):
        pass

    def options(self, id=None):
        return {"status": "oke"}    
    
    def get(self, id):
        qry = Products.query.get(id)
        if qry is not None:
            return marshal(qry, Products.response_fields), 200, {'Content-Type': 'application/json'}
        return {'status': 'Client Not Found'}, 404, {'Content-Type': 'application/json'}

    @jwt_required
    @seller_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', location='json', required=True)
        parser.add_argument('description', location='json', required=True)
        parser.add_argument('category_id', location='json', required=True)
        parser.add_argument('stock', location='json')
        parser.add_argument('unit_price', location='json', required=True)
        parser.add_argument('discount', location='json')
        parser.add_argument('url_foto', location='json')
        data = parser.parse_args()

        data['seller_id'] = get_jwt_claims()['id']

        product = Products(data['name'], data['description'], data['category_id'], data['stock'], data['unit_price'], data['discount'], data['seller_id'], data['url_foto'])
        db.session.add(product)
        db.session.commit()

        app.logger.debug('DEBUG : %s', product)

        return marshal(product, Products.response_fields), 200, {'Content-Type': 'application/json'}

    @jwt_required
    @seller_required
    def put(self,id):
        parser = reqparse.RequestParser()
        parser.add_argument('name', location='json', required=True)
        parser.add_argument('stock', location='json')
        parser.add_argument('category_id', location='json')
        parser.add_argument('description', location='json', required=True)
        parser.add_argument('unit_price', location='json', required=True)
        parser.add_argument('discount', location='json')
        parser.add_argument('url_foto', location='json')
        args = parser.parse_args()
        
        qry = Products.query.get(id)
        current_seller_id = get_jwt_identity()
        if qry.seller_id != current_seller_id:
            return {"message": "You have no permission to edit this product."}, 405

        qry.name = args['name']
        qry.description = args['description']
        qry.category_id = args['category_id']
        qry.stock = args['stock']
        qry.unit_price = args['unit_price']
        qry.discount = args['discount']
        qry.url_foto = args['url_foto']
        db.session.commit()

        return marshal(qry, Products.response_fields), 200, {'Content-Type': 'application/json'}

    @jwt_required
    @seller_required
    def delete(self, id):
        qry = Products.query.get(id)
        if qry is None:
            return {'status': 'Client Not Found'}, 404, {'Content-Type': 'application/json'}

        db.session.delete(qry)
        db.session.commit()

        return {'status': 'Client Deleted'}, 200, {'Content-Type': 'application/json'}

    def patch(self):
        return 'Not yet implemented', 501

class ProductList(Resource):

    def __init__(self):
        pass

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('p', type=int, location='args', default=1)
        parser.add_argument('rp', type=int, location='args', default=25)
        parser.add_argument('description', location='args', choices=('male', 'female'))
        parser.add_argument('orderby', location='args', choices=('unit_price', 'description'))
        parser.add_argument('sort', location='args', choices=('asc', 'desc'))
        args = parser.parse_args()

        offset = (args['p'] * args['rp']) - args['rp']

        qry = Products.query

        if args['description'] is not None:
            qry = qry.filter_by(description=args['description'])

        if args['orderby'] is not None:
            if args['orderby'] == 'unit_price':
                if args['sort'] == 'desc':
                    qry = qry.order_by(desc(Products.id)) # bisa gini
                else:
                    qry = qry.order_by((Products.id))
            elif args['orderby'] == 'description':
                if args['sort'] == 'desc':
                    qry = qry.order_by((Products.id).desc()) # bisa juga gini   
                else:
                    qry = qry.order_by((Products.id))

        rows = []
        for row in qry.limit(args['rp']).offset(offset).all():
            rows.append(marshal(row, Products.response_fields))
        return rows, 200, {'Content-Type': 'application/json'}

api.add_resource(ProductList, '/list')
api.add_resource(ProductResource, '', '/<id>')

