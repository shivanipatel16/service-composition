import random
import string

from flask import Response
from flask_cors import CORS
from flask import Flask, request
import logging
import grequests
from datetime import datetime
import requests
import json
import utils.rest_utils as rest_utils
from middleware.service_factory import get_service_factory_url
import copy

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = Flask(__name__)
CORS(app)

@app.route('/')
def hello_world():
    res = '<u> hi bubss :))) </u>'
    return Response(res, status=200, content_type="application/json")

@app.route('/api/login/v2/new_user', methods=["POST"])
def insert_user():
    """
    first adds new user data to the db, then adds the address,
    and then updates the address_id in the user table
    """
    try:

        inputs = rest_utils.RESTContext(request)
        template = inputs.data

        user_service_url = get_service_factory_url("login", "users")
        address_service_url = get_service_factory_url("login", "address")

        headers = {'Accept-Encoding': 'UTF-8', 'Content-Type': 'application/json', 'Accept': '*/*'}

        # post to user
        user_template = copy.deepcopy(template)
        user_template['address_id'] = 0
        del user_template['address']

        user_data = json.dumps(user_template, default=str)
        response_from_user_post = requests.post(user_service_url, data=user_data, headers=headers)
        res_from_user_post = response_from_user_post.json()
        print(res_from_user_post)

        # post to address
        user_id = res_from_user_post["data"]["user_id"]
        address_template = template["address"]
        address_template["user_id"] = user_id

        address_data = json.dumps(address_template, default=str)
        response_from_address_post = requests.post(address_service_url, data=address_data, headers=headers)
        res_from_address_post = response_from_address_post.json()
        print(res_from_address_post)

        # put to user with actual address_id
        address_update_template = dict()
        address_update_template["address_id"] = res_from_address_post["data"]["address_id"]
        address_update_data = json.dumps(address_update_template)
        response_from_user_put = requests.put("{}/{}".format(user_service_url, user_id), data=address_update_data,
                                              headers=headers)
        res_from_user_put = response_from_user_put.json()
        print(res_from_user_put)

        res = {"data": {"user_id": user_id}, "location": 'api/login/users/{}'.format(user_id)}
        res = json.dumps(res, default=str)
        rsp = Response(res, status=201, content_type="application/json")
        return rsp

    except Exception as e:
        return Response("Error. " + str(e), status=500, content_type="text/plain")


@app.route('/api/orders/v2/<user_id>', methods=["GET"])
def get_orders_by_userid(user_id):
    """
    compiles all orders by a particular user into a list of orders placed
    """
    try:
        inputs = rest_utils.RESTContext(request)
        rest_utils.log_request("resource_by_id", inputs)

        if inputs.method == "GET":

            primary_service_url = get_service_factory_url("order", "info")
            secondary_service_url = get_service_factory_url("order", "orders")
            user_template = {"user_id": user_id}

            r = requests.get(primary_service_url, params=user_template)
            res = r.json()
            orders = res["data"]

            rs = list()
            for order in orders:
                order_template = {"order_id": order["order_id"]}
                rs.append(grequests.get(secondary_service_url, params=order_template))

            responses = grequests.map(rs)
            if any(response.status_code != 200 for response in responses):
                print("Error with:")

            for i in range(len(orders)):
                orders[i]["order"] = responses[i].json()["data"]

            res = json.dumps(res, default=str)
            rsp = Response(res, status=200, content_type="application/json")
            return rsp
        else:
            return Response("Method Not Implemented.", status=501, content_type="text/plain")

    except Exception as e:
        return Response("Server Error. " + str(e), status=500, content_type="text/plain")


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
    pass