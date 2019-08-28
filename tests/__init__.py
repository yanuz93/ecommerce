import pytest, json, logging
from flask import Flask, request, json
from blueprints import app
from app import cache
import json

def call_client(request):
    client = app.test_client()
    return client

@pytest.fixture
def client(request):
    return call_client(request)

def create_token_buyer():
    token = cache.get('token-buyer')
    if token is None:
        data = {
            'email': 'buyer_1',
            'password': 'buyer1'
        }

        req = call_client(request)
        res = req.post('/signin',
                        data=json.dumps(data),
                        content_type='application/json')
        res_json = json.loads(res.data)

        logging.warning('RESULT : %s', res_json)

        assert res.status_code == 200

        cache.set('token-buyer', res_json['token'], timeout=60)

        return res_json['token']
    else:
        return token


def create_token_seller():
    token = cache.get('token-seller')
    if token is None:
        data = {
            'client_key': 'seller_2',
            'client_secret': 'seller2'
        }

        req = call_client(request)
        res = req.post('/signin',
                        data=json.dumps(data),
                        content_type='application/json')

        res_json = json.loads(res.data)

        logging.warning('RESULT : %s', res_json)

        assert res.status_code == 200

        cache.set('token-seller', res_json['token'], timeout=60)

        return res_json['token']
    else:
        return token
        
            
