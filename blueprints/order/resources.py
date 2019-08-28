from flask import Blueprint, jsonify
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
    
    def options(self, id=None):
        return {"status": "oke"}

    @jwt_required
    # @customer_required
    def get(self):
        def jawab_request(status_id):
            current_user = get_jwt_identity()
            order = Orders.query.filter_by(customer_id = current_user, status = status_id).first()
            if order == None:
                ans = {}
                ans["message"] = "SUCCESS"
                ans["total_qty"] = 0
                ans["total_price"] = 0
                ans["rincian"] = []
                return ans, 200

            # only order detail status true is taken since false means deleted 
            detail = OrderDetails.query.filter_by(order_id = order.id, status = True)
        
            ans = {}
            ans["message"] = "SUCCESS"
            ans["total_qty"] = order.total_qty
            ans["total_price"] = order.total_price
            rows = []
            for row in detail.all():
                isi_data = marshal(row, OrderDetails.response_fields)
                isi_data['product_name'] = Products.query.get(row.product_id).name
                isi_data['seller_name'] = Sellers.query.get(Products.query.get(row.product_id).seller_id).name
                isi_data['foto_product'] = Products.query.get(row.product_id).url_foto
                rows.append(isi_data)
            
            ans['rincian'] = rows
            return ans, 200
        
        parser = reqparse.RequestParser()
        parser.add_argument('status', type=int, location= 'args')
        args = parser.parse_args()
        if args['status'] == 10:
            return jawab_request(10)
        elif args['status'] == 20:
            return jawab_request(20)
        else:
            return jawab_request(30)

    @jwt_required
    # @customer_required
    def post(self):
        # add product to cart by customer id
        current_user = get_jwt_identity()
        order = Orders.query.filter_by(customer_id = current_user, status = 10).first()
        parser = reqparse.RequestParser()

        # if no cart found, create new with initial qty and price 0 plus status 10
        if order == None:
            order = Orders(customer_id = current_user, total_qty=0, total_price=0, status=10)
            db.session.add(order)
            db.session.commit()
        
        # if found one, add order detail from list. params : qty, product id, status
        # status: 10 > cart, 20 > checkout, 30 > done
        parser.add_argument('product_id', type=int, location='json')
        parser.add_argument('qty', type=int, location='json')
        parser.add_argument('status', type=int, location='json', choices=(10, 20, 30), default=10)
        args = parser.parse_args()

        if args['qty'] < 0:
            return {msg: "Jumlah barang tidak boleh negatif!"}, 303

        order_id = order.id
        price = Products.query.get(args['product_id']).unit_price

        detail = OrderDetails.query.filter_by(order_id = order_id, product_id = args['product_id'], status = True).first()
        if detail == None:
            detail = OrderDetails(order_id = order_id, product_id = args['product_id'], qty = args['qty'], price = price, status=True)
        else:
            detail.qty = detail.qty + args['qty']
            detail.updatedAt = db.func.current_timestamp()
        db.session.add(detail)
        db.session.commit()

        order.total_qty = order.total_qty + args['qty']
        order.total_price = order.total_price + (price*args['qty'])
        order.updatedAt = db.func.current_timestamp()
        db.session.add(order)
        db.session.commit()

        return {"message": "SUCCESS"}, 200

    @jwt_required
    def patch(self, id):
        current_user = get_jwt_identity()
        order = Orders.query.filter_by(customer_id = current_user, status = 10).first()

        parser = reqparse.RequestParser()
        parser.add_argument("action", type= str, help= 'action not exist', location= 'json', choices= ("ubah_qty", "bayar", "delete"), required= False)
        parser.add_argument("new_qty", type= str, help= 'action not exist', location= 'json', default=0)
        args = parser.parse_args()

        # ubah jumlah barang di cart
        if args['action'] == "ubah_qty":
            price = Products.query.get(id).unit_price
            order.total_qty = args['new_qty']
            order.total_price = price * args['new_qty']
            order.updatedAt = db.func.current_timestamp()
            db.session.add(order)
            db.session.commit()

            detail = OrderDetails.query.filter_by(order_id = order.id, product_id = id, status= True).first()
            detail.qty = detail.qty + 1
            detail.updatedAt = db.func.current_timestamp()
            db.session.add(detail)
            db.session.commit()
        
        # proses checkout dilakukan dengan mengubah status order menjadi 20
        elif args['action'] == "bayar":
            detail = OrderDetails.query.filter_by(order_id = order.id, product_id = id, status= True).first()
            order.status = 20
            order.updatedAt = db.func.current_timestamp()
            Products.query.get(id).stock -= detail.qty
            db.session.add(order)
            db.session.commit()

        # proses delete product dari cart dilakukan dengan mengubah status order
        # detail menjadi false
        elif args['action'] == "delete":
            price = Products.query.get(id).unit_price
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

    def options(self):
        return {"status": "oke"}

    @jwt_required
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('p', type=int, location='args', default=1)
        parser.add_argument('rp', type=int, location='args', default=25)
        args = parser.parse_args()

        offset = (args['p'] * args['rp']) - args['rp']
        current_customer = get_jwt_identity()
        qry = Orders.query.filter_by(customer_id = current_customer)

        rows = []
        for row in qry.limit(args['rp']).offset(offset).all():
            rows.append(marshal(row, Orders.response_fields))
        return rows, 200, {'Content-Type': 'application/json'}

api.add_resource(OrderList, '/list')
api.add_resource(OrderResource, '', '/<id>')
