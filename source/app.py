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
from chalice import Chalice, AuthResponse, Response, CORSConfig

# aws clients imports
from chalicelib.aws_clients import secrets_manager_client as sm_client

# custom services imports
from chalicelib import reservations_service as rs
from chalicelib import auth_service as auth
from chalicelib import user_info_service as uis

# init logging client
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# environment variable is set via chalice config; set global envs
ENV = os.environ["RUN_ENV"] if "RUN_ENV" in list(os.environ) else "sandbox"
with open(f"chalicelib/configs/{ENV}.json") as f:
    CONFIG = json.load(f)

CORS = CORSConfig(
    allow_origin="*",
    allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Origin"],
    max_age=600,
    expose_headers=[],
    allow_credentials=True
)

# init the reservations service
rs.init_service(
    env_config=CONFIG
)

auth.init_service(
    env_config=CONFIG
)

uis.init_service(
    env_config=CONFIG
)

# init chalice app
app = Chalice(app_name='gularte-cabin-calendar-backend')

"""
AUTHORIZERS
"""


@app.authorizer()
def token_auth(auth_request):
    # super secure and secret local dev authorization
    if ENV == "local" and auth_request.auth_type == "TOKEN":
        if auth_request.token == CONFIG["secret"]:
            return AuthResponse(routes=["/*"], principal_id="user")
        else:
            return AuthResponse(routes=[], principal_id="user")

    if auth_request.auth_type == "TOKEN" and auth_request.token == sm_client.get_secret(CONFIG["secret_id"],
                                                                                        CONFIG["secret_key"],
                                                                                        CONFIG["secret_region"]):
        logger.info({"AuthType": auth_request.auth_type, "Success": True})
        return AuthResponse(routes=["/*"], principal_id="user")
    else:
        logger.info({"AuthType": auth_request.auth_type, "Success": False})
        return AuthResponse(routes=[], principal_id="user")


"""
HEALTHCHECK
"""


@app.route(
    "/healthcheck",
    methods=["GET"],
    authorizer=token_auth
)
def healthcheck() -> Response:
    """
    A simple endpoint to perform system healthcheck

    :return: Chalice response object.
    """
    # log request and return
    log_request(app.current_request.to_dict(), app.current_request.json_body)
    return Response(status_code=200, body={"message": "I am healthy."})


"""
AUTHORIZATION CONTROLLER
"""


@app.route(
    "/authorization",
    methods=["GET", "POST"],
    authorizer=token_auth,
    cors=CORS
)
def authorize() -> Response:
    # log request
    # log_request(app.current_request.to_dict(), app.current_request.json_body)
    if app.current_request.method == "GET":
        if not app.current_request.query_params.get("at"):
            return Response(
                status_code=400,
                body={
                    "error": "No access token provided in the current request's query parameters."
                }
            )

        return auth.get_user_via_access_token(
            access_token=app.current_request.query_params["at"]
        )

    if app.current_request.method == "POST":
        return auth.init_auth_flow(
            client_id=app.current_request.json_body["client_id"],
            username=app.current_request.json_body["username"],
            password_hash=app.current_request.json_body["password"]
        )


@app.route(
    "/user_info",
    methods=["GET"],
    authorizer=token_auth,
    cors=CORS
)
def user_info() -> Response:
    if app.current_request.method == "GET":
        if not app.current_request.query_params.get("uguid"):
            return Response(
                status_code=400,
                body={
                    "error": "the parameter 'uguid' is not in the request's query parameters."
                }
            )

        return uis.get_userinfo(app.current_request.query_params["uguid"])
"""
RESERVATIONS CONTROLLER
"""


@app.route(
    "/reservations",
    methods=["GET", "POST", "PUT", "DELETE"],
    authorizer=token_auth,
    cors=CORS
)
def reservation() -> Response:
    """
    endpoint to handle all reservation based CRUD tasks.

    :return: Chalice response object.
    """
    # log incoming request
    # log_request(app.current_request.to_dict(), app.current_request.json_body)

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
                    "error": "Query params were not empty but, did not have an 'guid' attribute. Please read the OpenAPI"
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


def log_request(request: dict, body: dict or None) -> None:
    logger.warning(f"Path: {request['path']}; \n"
                   f"Method: {request['method']}; \n"
                   f"URI Params: {json.dumps(request['uri_params'])}; \n"
                   f"Query Params: {json.dumps(request['query_params'])}; \n"
                   f"Body: {json.dumps(body)}"
                   )
