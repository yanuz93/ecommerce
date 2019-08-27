from flask import Flask, request
from flask_migrate import Migrate, MigrateCommand
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
import json
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt_claims
from datetime import timedelta
from functools import wraps

###################################
# Define app
###################################
app = Flask(__name__)

###################################
# JWT
###################################

app.config['JWT_SECRET_KEY'] = 'Thoi290a}kdfa12aQ~aAasK?aJqw<q21'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)

jwt = JWTManager(app)

# Buat Decorator untuk admin
def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt_claims()
        if not claims['status'] != -1:
            return {'status': 'FORBIDDEN', 'message': 'Only for Administrators'}, 403
        else:
            return f(*args, **kwargs)
    return wrapper

# Buat Decorator untuk seller
def seller_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt_claims()
        if claims['status'] != 99 :
            return {'status': 'FORBIDDEN', 'message': 'Only for Sellers'}, 403
        else:
            return f(*args, **kwargs)
    return wrapper

# Buat Decorator untuk customer
def customer_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt_claims()
        if claims['status'] != 999:
            return {'status': 'FORBIDDEN', 'message': 'Only for Customers'}, 403
        else:
            return f(*args, **kwargs)
    return wrapper

###################################
# Setting up database(s)
###################################

app.config['APP_DEBUG'] = True
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:matematika@localhost:3306/tokodaring'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:mathUGM11@ecommercedb.cpqwkx2hzvh3.ap-southeast-1.rds.amazonaws.com:3306/tokodaring'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app, db)
manager.add_command('db', MigrateCommand)

###################################
# Set up middleware
###################################
@app.after_request
def afterRequest(response):
    try:
        datarequest = request.get_json()
    except Exception as exc:
        datarequest = request.args.to_dict()
    app.logger.warning("REQUEST LOG\t%s", json.dumps({'method': request.method, 'code': response.status, 'uri': request.full_path, 'request': datarequest, 'response': json.loads(response.data.decode('utf-8'))}))
    return response

from blueprints.seller.resources import bp_seller
from blueprints.category.resources import bp_category
from blueprints.customer.resources import bp_customer
from blueprints.product.resources import bp_product
from blueprints.order.resources import bp_order
from .seller_auth import bp_seller_auth
from .customer_auth import bp_customer_auth

app.register_blueprint(bp_seller, url_prefix='/seller')
app.register_blueprint(bp_customer, url_prefix='/customer')
app.register_blueprint(bp_product, url_prefix='/product')
app.register_blueprint(bp_order, url_prefix='/order')
app.register_blueprint(bp_customer_auth, url_prefix='/customer/login')
app.register_blueprint(bp_seller_auth, url_prefix='/seller/login')
app.register_blueprint(bp_category, url_prefix='/category')

# db.drop_all()
db.create_all()
