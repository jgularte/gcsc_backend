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

# init logging client
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# environment variable is set via chalice config; set global envs
ENV = os.environ["MICROSVC_ENV"] if "MICROSVC_ENV" in list(os.environ) else "sandbox"
with open(f"chalicelib/configs/{ENV}.json") as f:
    CONFIG = json.load(f)

# init chalice app
app = Chalice(app_name='gularte-cabin-calendar-backend')


@app.route("/healthcheck", methods=["GET"])
def healthcheck():
    return Response(status_code=200, body={"message": "I am healthy."})


@app.route("/reservations", methods=["GET", "POST", "PUT", "DELETE"])
def reservation():
    if app.current_request.method == "GET":
        # GET reservation; if 'id' query param is available, use to get a single res. if no qp's then list all res.
        if not app.current_request.query_params:
            pass
        elif app.current_request.query_params.get("id"):
            pass
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
            pass
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
            pass
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
        if app.current_request.query_params.get("id"):
            pass
        else:
            return Response(
                status_code=400,
                body={
                    "error": "Query params did not have an 'id' attribute. Please read the OpenAPI"
                             " document on how to use this endpoint."
                }
            )
