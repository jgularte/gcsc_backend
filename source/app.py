"""
filename: app.py
author: Jack Gularte
date: Oct. 12 2020

Root level file for chalice application. Holds the endpoint handlers
"""

# standard imports
import logging
import os
import json

# chalice imports
from chalice import Chalice, AuthResponse, Response

# aws clients imports
from chalicelib.aws_clients import secrets_manager_client as sm_client

# custom services imports
from chalicelib import reservations_service as rs

# init logging client
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# environment variable is set via chalice config; set global envs
ENV = os.environ["RUN_ENV"] if "RUN_ENV" in list(os.environ) else "sandbox"
with open(f"chalicelib/configs/{ENV}.json") as f:
    CONFIG = json.load(f)

# init chalice app
app = Chalice(app_name='gularte-cabin-calendar-backend')


"""
AUTHORIZERS
"""


@app.authorizer()
def token_auth(auth_request):
    if auth_request.auth_type == "TOKEN" and auth_request.token == sm_client.get_secret(CONFIG["secret_id"], CONFIG["secret_key"], CONFIG["secret_region"]):
        return AuthResponse(routes=["/*"], principal_id="user")
    else:
        return AuthResponse(routes=[], principal_id="user")


"""
HEALTHCHECK
"""


@app.route(
    "/healthcheck",
    methods=["GET", "POST"],
    authorizer=token_auth
)
def healthcheck():
    # log request and return
    log(app.current_request.to_dict(), app.current_request.json_body)
    return Response(status_code=200, body={"message": "I am healthy."})


"""
RESERVATIONS CONTROLLER
"""


@app.route(
    "/reservations",
    methods=["GET", "POST", "PUT", "DELETE"],
    authorizer=token_auth
)
def reservation():
    # log incoming request
    log(app.current_request.to_dict(), app.current_request.json_body)

    # perform routing based off request
    if app.current_request.method == "GET":
        # GET reservation; if 'id' query param is available, use to get a single res. if no params then list all res.
        if not app.current_request.query_params:
            return rs.list_reservations()
        elif app.current_request.query_params.get("guid"):
            return rs.get_reservation(
                reservation_guid=app.current_request.query_params["guid"]
            )
        else:
            return Response(
                status_code=400,
                body={
                    "error": "Query params were not empty but, did not have an 'id' attribute. Please read the OpenAPI"
                             " document on how to use this endpoint."
                }
            )
    elif app.current_request.method == "POST":
        # POST reservation; the reservation to create needs to be in the requests body
        if app.current_request.json_body:
            return rs.create_reservation(
                reservation=app.current_request.json_body
            )
        else:
            return Response(
                status_code=400,
                body={
                    "error": "The request's body was empty. "
                             "Please read the OpenAPI document on how to use this endpoint"
                }
            )
    elif app.current_request.method == "PUT":
        # PUT reservation; the reservation to update needs to be in the requests body
        # POST reservation; the reservation to create needs to be in the requests body
        if app.current_request.json_body:
            return rs.update_reservation(
                reservation=app.current_request.json_body
            )
        else:
            return Response(
                status_code=400,
                body={
                    "error": "The request's body was empty. "
                             "Please read the OpenAPI document on how to use this endpoint"
                }
            )
    else:
        # DELETE reservation; the 'id' query param indicates what reservation to delete
        if app.current_request.query_params.get("guid"):
            return rs.delete_reservation(
                reservation_guid=app.current_request.query_params["guid"]
            )
        else:
            return Response(
                status_code=400,
                body={
                    "error": "Query params did not have an 'id' attribute. Please read the OpenAPI"
                             " document on how to use this endpoint."
                }
            )


"""
HELPER FUNCTIONS
"""


def log(request: dict, body: dict or None) -> None:
    logger.info(f"Path: {request['path']}; \n"
                f"Method: {request['method']}; \n"
                f"URI Params: {json.dumps(request['uri_params'])}; \n"
                f"Query Params: {json.dumps(request['query_params'])}; \n"
                f"Body: {json.dumps(body)}"
                )
