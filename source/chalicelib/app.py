"""
filename: app.py
author: Jack Gularte
date: Oct. 12 2020

Root level file for chalice application. Holds the endpoint handlers
"""

# standard imports
import logging

# chalice imports
from chalice import Chalice, AuthResponse, Response

# init logging client
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# init chalice app
app = Chalice(app_name='gularte-cabin-calendar-backend')


@app.route("/healthcheck", methods=["GET"])
def healthcheck():
    return Response(status_code=200, body={"message": "I am healthy."})
