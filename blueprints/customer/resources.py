from flask import Blueprint
from flask_restful import Resource, Api, reqparse, marshal, inputs
from .models import Customers
from sqlalchemy import desc
from blueprints import app, db, customer_required, admin_required
from flask_jwt_extended import jwt_required, get_jwt_claims, get_jwt_identity

bp_customer = Blueprint('customers', __name__)
api = Api(bp_customer)

class CustomerResource(Resource):
    def __init__(self):
        pass
    
    def options(self, id=None):
        return {"status": "oke"}
        # pass

    @jwt_required
    def get(self):
        # if id == self.current_customer_id:
        current_user = get_jwt_identity()
        qry = Customers.query.get(current_user)
        if qry != None :
            return marshal(qry, Customers.response_fields), 200, {'Content-Type': 'application/json'}
        return {'message': 'Customer Not Found'}, 404, {'Content-Type': 'application/json'}

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', location='json', required=True)
        parser.add_argument('email', location='json', required=True)
        parser.add_argument('password', location='json', required=True)
        parser.add_argument('phone_number', location='json', required=True)
        parser.add_argument('address', location='json')
        parser.add_argument('sex', location='json')
        parser.add_argument('status', location='json', default=999)
        parser.add_argument('url_foto', location='json')
        data = parser.parse_args()

        qry = Customers.query.filter_by(email= data['email']).first()
        if qry != None:
            return {"message": "Email already taken"}, 406

        customer = Customers(data['name'], data['email'], data['password'], data['phone_number'], data['address'], data['sex'], data['status'], data['url_foto'])
        db.session.add(customer)
        db.session.commit()

        app.logger.debug('DEBUG : %s', customer)

        return marshal(customer, Customers.response_fields), 200, {'Content-Type': 'application/json'}

    @jwt_required
    @customer_required
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', location='json', required=True)
        parser.add_argument('email', location='json', required=True)
        parser.add_argument('password', location='json', required=True)
        parser.add_argument('phone_number', location='json', required=True)
        parser.add_argument('address', location='json', required=True)
        parser.add_argument('sex', location='json')
        parser.add_argument('url_foto', location='json')
        args = parser.parse_args()

        current_customer_id = get_jwt_claims()['id']
        
        qry = Customers.query.get(current_customer_id)
        qry.name = args['name']
        qry.email = args['email']
        qry.password = args['password']
        qry.address = args['address']
        qry.sex = args['sex']
        qry.phone_number = args['phone_number']
        qry.url_foto = args['url_foto']
        db.session.commit()

        return marshal(qry, Customers.response_fields), 200, {'Content-Type': 'application/json'}

    @admin_required
    def delete(self, id):
        qry = Customers.query.get(id)
        if qry is None:
            return {'status': 'Customer Not Found'}, 404, {'Content-Type': 'application/json'}

        db.session.delete(qry)
        db.session.commit()

        return {'status': 'Customer Deleted'}, 200, {'Content-Type': 'application/json'}

    def patch(self):
        return 'Not yet implemented', 501

class CustomerList(Resource):

    def __init__(self):
        pass
    def options(self, id=None):
        return {"status": "oke"}
    @admin_required
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('p', type=int, location='args', default=1)
        parser.add_argument('rp', type=int, location='args', default=25)
        parser.add_argument('sex', location='args', choices=('male', 'female'))
        parser.add_argument('orderby', location='args', choices=('id', 'name', 'email', 'sex'))
        parser.add_argument('sort', location='args', choices=('asc', 'desc'))
        args = parser.parse_args()

        offset = (args['p'] * args['rp']) - args['rp']

        qry = Customers.query

        if args['sex'] is not None:
            qry = qry.filter_by(sex=args['sex'])

        def urut(kriteria):
            if args['sort'] == 'desc':
                    qry = qry.order_by(desc(kriteria))
            else:
                qry = qry.order_by((kriteria))

        if args['orderby'] is not None:
            if args['orderby'] == 'id':
                urut(Customers.id)
            elif args['orderby'] == 'name':
                urut(Customers.name)
            elif args['orderby'] == 'email':
                urut(Customers.email)
            elif args['orderby'] == 'sex':
                urut(Customers.sex)

        rows = []
        for row in qry.limit(args['rp']).offset(offset).all():
            rows.append(marshal(row, Customers.response_fields))
        return rows, 200, {'Content-Type': 'application/json'}

api.add_resource(CustomerList, '/list')
api.add_resource(CustomerResource, '', '/<id>')

