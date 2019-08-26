from flask import Blueprint
from flask_restful import Resource, Api, reqparse, marshal, inputs
from .models import Sellers
from sqlalchemy import desc
from blueprints import app, db, seller_required, admin_required
from flask_jwt_extended import jwt_required, get_jwt_claims

bp_seller = Blueprint('sellers', __name__)
api = Api(bp_seller)

class SellerResource(Resource):
    
    def __init__(self):
        pass
    
    @jwt_required
    def get(self, id):
        # if id == self.current_seller_id:
        qry = Sellers.query.get(id)
        if qry != None :
            return marshal(qry, Sellers.response_fields), 200, {'Content-Type': 'application/json'}
        return {'message': 'Seller Not Found'}, 404, {'Content-Type': 'application/json'}

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', location='json', required=True)
        parser.add_argument('email', location='json', required=True)
        parser.add_argument('password', location='json', required=True)
        parser.add_argument('phone_number', location='json', required=True)
        parser.add_argument('city', location='json')
        parser.add_argument('address', location='json', required=True)
        parser.add_argument('postcode', location='json', required=True)
        parser.add_argument('province', location='json')
        parser.add_argument('status', location='json', default=99)
        parser.add_argument('url_foto', location='json')
        data = parser.parse_args()

        
        qry = Sellers.query.filter_by(email= data['email']).first()
        if qry != None:
            return {"message": "Email already taken"}, 406

        seller = Sellers(data['name'], data['email'], data['password'], data['phone_number'], data['address'], data['city'], data['province'], data['postcode'], data['status'], data['url_foto'])
        db.session.add(seller)
        db.session.commit() 

        app.logger.debug('DEBUG : %s', seller)

        return marshal(seller, Sellers.response_fields), 200, {'Content-Type': 'application/json'}

    @jwt_required
    @seller_required
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', location='json', required=True)
        parser.add_argument('email', location='json', required=True)
        parser.add_argument('password', location='json', required=True)
        parser.add_argument('phone_number', location='json', required=True)
        parser.add_argument('city', location='json', required=True)
        parser.add_argument('province', location='json', required=True)
        parser.add_argument('postcode', location='json', required=True)
        parser.add_argument('address', location='json', required=True)
        parser.add_argument('status', location='json', default=999)
        parser.add_argument('url_foto', location='json')
        args = parser.parse_args()
        
        current_seller_id = get_jwt_claims()['id']
        qry = Sellers.query.get(current_seller_id)
        qry.name = args['name']
        qry.email = args['email']
        qry.password = args['password']
        qry.address = args['address']
        qry.city = args['city']
        qry.province = args['province']
        qry.postcode = args['postcode']
        qry.phone_number = args['phone_number']
        qry.url_foto = args['url_foto']
        db.session.commit()

        return marshal(qry, Sellers.response_fields), 200, {'Content-Type': 'application/json'}

    @admin_required
    def delete(self, id):
        qry = Sellers.query.get(id)
        if qry is None:
            return {'status': 'Seller Not Found'}, 404, {'Content-Type': 'application/json'}

        db.session.delete(qry)
        db.session.commit()

        return {'status': 'Seller Deleted'}, 200, {'Content-Type': 'application/json'}

    def patch(self):
        return 'Not yet implemented', 501

class SellerList(Resource):

    def __init__(self):
        pass

    @admin_required
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('p', type=int, location='args', default=1)
        parser.add_argument('rp', type=int, location='args', default=25)
        parser.add_argument('city', location='args', choices=('male', 'female'))
        parser.add_argument('orderby', location='args', choices=('id', 'name', 'email', 'city'))
        parser.add_argument('sort', location='args', choices=('asc', 'desc'))
        args = parser.parse_args()

        offset = (args['p'] * args['rp']) - args['rp']

        qry = Sellers.query

        if args['city'] is not None:
            qry = qry.filter_by(city=args['city'])

        def urut(kriteria):
            if args['sort'] == 'desc':
                    qry = qry.order_by(desc(kriteria))
            else:
                qry = qry.order_by((kriteria))

        if args['orderby'] is not None:
            if args['orderby'] == 'id':
                urut(Sellers.id)
            elif args['orderby'] == 'name':
                urut(Sellers.name)
            elif args['orderby'] == 'email':
                urut(Sellers.email)
            elif args['orderby'] == 'city':
                urut(Sellers.city)

        rows = []
        for row in qry.limit(args['rp']).offset(offset).all():
            rows.append(marshal(row, Sellers.response_fields))
        return rows, 200, {'Content-Type': 'application/json'}

api.add_resource(SellerList, '/list')
api.add_resource(SellerResource, '', '/<id>')
