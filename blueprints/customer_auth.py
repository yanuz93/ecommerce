from flask import Blueprint
from flask_restful import Api, Resource, reqparse, marshal
import sys, json, datetime, math
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt_claims
from blueprints.customer.resources import CustomerResource, CustomerList
from blueprints.customer.models import Customers

bp_customer_auth = Blueprint('customer_auth', __name__)
api = Api(bp_customer_auth)

### Resources
class CreateCustomerTokenResources(Resource):

    def options(self, id=None):
        return {"status": "oke"}

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', location= 'json', required= True)
        parser.add_argument('password', location= 'json', required= True)

        args = parser.parse_args()

        # get data users by username and password
        qry = Customers.query.filter_by( email= args['email'], password= args['password']).first()
        
        # check is user with username and password have account ?
        # if not return 401
        if qry == None:
            return {"message": "UNAUTHORIZED"}, 401
        
        # if have account create token for him
        customer_data = marshal(qry, Customers.response_fields)
        customer_data.pop("password")
        token = create_access_token(identity= qry.id, user_claims= customer_data)
        return {'token': token}, 200

    # @jwt_required
    # def post(self):
    #     claims = get_jwt_claims()
    #     return {'claims': claims}, 200

class RefreshCustomerTokenResources(Resource):
    @jwt_required
    def post(self):
        current_user = get_jwt_identity()
        token = create_access_token(identity=current_user)
        return {'token': token}, 200
        

api.add_resource(CreateCustomerTokenResources, '')
api.add_resource(RefreshCustomerTokenResources, '/refresh')
