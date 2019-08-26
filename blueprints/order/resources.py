from flask import Blueprint
from flask_restful import Resource, Api, reqparse, marshal, inputs
from .models import Orders, OrderDetails
from ..product.models import Products
from ..seller.models import Sellers
from sqlalchemy import desc
from blueprints import app, db, customer_required
from flask_jwt_extended import jwt_required, get_jwt_claims, get_jwt_identity

bp_order = Blueprint('Orders', __name__)
api = Api(bp_order)

class OrderResource(Resource):
    def __init__(self):
        pass
    
    @jwt_required
    # @customer_required
    def get(self):
        current_user = get_jwt_identity()

        parser = reqparse.RequestParser()
        parser.add_argument("status", type= inputs.boolean, help= 'status key must be boolean and exist', location= 'args', default= False)
        args = parser.parse_args()
        
        order = Orders.query

        if args['status'] == False:
            order = order.filter_by(customer_id = current_user).filter_by(status = False).first()
            if order == None:
                ans = {}
                ans["message"] = "SUCCESS"
                ans["total_qty"] = 0
                ans["total_price"] = 0
                ans["data"] = []
                return ans, 200

            detail = OrderDetails.query.filter_by(order_id = order.id, status = True)
            
            ans = {}
            ans["message"] = "SUCCESS"
            ans["total_qty"] = order.total_qty
            ans["total_price"] = order.total_price
            rows = []
            for row in detail.all():
                isi_data = OrderDetails.response_fields
                marshal_row = marshal(row, isi_data)
                isi_data['product_name'] = Products.query.get(marshal_row['product_id'])['name']
                isi_data['seller_name'] = Sellers.query.get(get(marshal_row.product_id)['seller_id'])['name']
                rows.append(marshal(row, isi_data))
            
            ans["data"] = rows
            return ans, 200

        elif args['status'] == True:
            order = order.filter_by(customer_id = current_user, status = True).order_by('updatedAt').all()
            
            all_data = []
            for data in order:
                ans = marshal(data, Orders.response_fields)
                
                detail = OrderDetails.query.filter_by(order_id = data.id, status = True)
                rows = []
                for row in detail.all():
                    rows.append(marshal(row, OrderDetails.response_fields))
                
                ans["datas"] = rows
                all_data.append(ans)
            
            return all_data, 200

    @jwt_required
    # @customer_required
    def post(self, id):
        current_user = get_jwt_identity()
        order = Orders.query.filter_by(customer_id = current_user, status = True).first()
        if order == None:
            order = Orders(customer_id = current_user, total_qty=0, total_price=0, status=True)
            db.session.add(order)
            db.session.commit()
        
        order_id = order.id

        price = Products.query.get(id).unit_price

        detail = OrderDetails.query.filter_by(order_id = order_id, product_id = id, status = True).first()
        if detail == None:
            detail = OrderDetails(order_id = order_id, product_id = id, qty = 1, price = price)
        else:
            detail.qty = detail.qty + 1
            detail.updatedAt = db.func.current_timestamp()
        db.session.add(detail)
        db.session.commit()

        order.total_qty = order.total_qty + 1
        order.total_price = order.total_price + price
        order.updatedAt = db.func.current_timestamp()
        db.session.add(order)
        db.session.commit()

        return {"message": "SUCCESS"}, 200

    @customer_required
    def patch(self, id):

        current_user = get_jwt_identity()
        order = Orders.query.filter_by(customer_id = current_user, status = False).first()

        parser = reqparse.RequestParser()
        parser.add_argument("action", type= str, help= 'action not exist', location= 'json', choices= ("tambah_qty", "kurang_qty", "bayar", "delete"), required= False)
        args = parser.parse_args()

        if args['action'] == "tambah_qty":
            price = Products.query.get(id).price
            order.total_qty = order.total_qty + 1
            order.total_price = order.total_price + price
            order.updatedAt = db.func.current_timestamp()
            db.session.add(order)
            db.session.commit()

            detail = OrderDetails.query.filter_by(order_id = order.id, product_id = id, status= True).first()
            detail.qty = detail.qty + 1
            detail.updatedAt = db.func.current_timestamp()
            db.session.add(detail)
            db.session.commit()

        elif args['action'] == "kurang_qty":
            price = Products.query.get(id).price
            order.total_qty = order.total_qty - 1
            order.total_price = order.total_price - price
            order.updatedAt = db.func.current_timestamp()
            db.session.add(order)
            db.session.commit()

            detail = OrderDetails.query.filter_by(order_id = order.id, product_id = id, status= True).first()
            detail.qty = detail.qty - 1
            detail.updatedAt = db.func.current_timestamp()
            db.session.add(detail)
            db.session.commit()

        elif args['action'] == "bayar":
            order.status = True
            order.updatedAt = db.func.current_timestamp()
            db.session.add(order)
            db.session.commit()

        elif args['action'] == "delete":
            price = Products.query.get(id).price

            detail = OrderDetails.query.filter_by(order_id = order.id, product_id = id, status= True).first()
            detail.status = False
            detail.updatedAt = db.func.current_timestamp()
            db.session.add(detail)
            db.session.commit()

            order.total_qty = order.total_qty - detail.qty
            order.total_price = order.total_price - (detail.qty * price)
            order.updatedAt = db.func.current_timestamp()
            db.session.add(order)
            db.session.commit()

        return {'message': "SUCCESS"}, 200

class OrderList(Resource):
    def __init__(self):
        pass

    @jwt_required
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('p', type=int, location='args', default=1)
        parser.add_argument('rp', type=int, location='args', default=25)
        # parser.add_argument('status', location='args', choices=(10, 20, 30))
        args = parser.parse_args()

        offset = (args['p'] * args['rp']) - args['rp']
        current_customer = get_jwt_identity()
        qry = Orders.query.filter_by(customer_id = current_customer)

        # if args['status'] is not None:
        #     qry = qry.filter_by(status=args['status'])

        rows = []
        for row in qry.limit(args['rp']).offset(offset).all():
            rows.append(marshal(row, Orders.response_fields))
        return rows, 200, {'Content-Type': 'application/json'}

api.add_resource(OrderList, '/list')
api.add_resource(OrderResource, '', '/<id>')
