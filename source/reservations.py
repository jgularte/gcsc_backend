# standard imports
import logging
import json
import sys
from uuid import uuid4
from os import environ

# internal imports
from aws_clients.dynamodb_client import DynamoDBClient

"""
GLOBAL VARIABLES TO REDUCE LAMBDA COST/INCREASE SPEED
"""
# declare logger
LOGGER = None
# prep config
CONFIG = None
# prep aws clients
RESERVATION_TABLE = None


def handler(event, context):
    """
    Lambda handler used as entry point
    :param event: json event object
    :param context: json lambda context object
    :return: json operation result
    """
    # if config null, initialize env
    if not CONFIG:
        environment_setup()

    if event["httpMethod"] == "GET":
        # if query parameters
        if event["pathParameters"]:
            return get_reservation(event)
        # if no query params, then do a full list
        return list_reservations()
    elif event["httpMethod"] == "POST":
        return create_reservation(event)
    elif event["httpMethod"] == "PUT":
        return update_reservation(event)
    elif event["httpMethod"] == "DELETE":
        return delete_reservation(event)
    else:
        return {
            "statusCode": 404,
            "body": {
                "message": "Method not supported at this endpoint"
            }
        }


def environment_setup():
    """
    Function used to set up run environment if the lambda is cold. will set only global variables.
    :return: None
    """
    # set globals
    global CONFIG, RESERVATION_TABLE, LOGGER

    # initialize logger
    LOGGER = logging.getLogger(__name__)
    LOGGER.setLevel(logging.INFO)

    # set up config
    # get run environment
    # local dynamodb will be found under a different environment variable via sam local
    if "AWS_SAM_LOCAL" in environ.keys():
        config_location = "reservations/local_config.json"

    elif "environment" in environ.keys():

        if environ["environment"] == "sandbox":
            config_location = "reservations/sandbox_config.json"
        elif environ["environment"] == "production":
            config_location = "reservations/production_config.json"
        else:
            LOGGER.error("The environment provided is not sandbox or production. Exiting....")
            sys.exit(1)
    else:
        LOGGER.error("The environment variable is not set. Exiting....")
        sys.exit(1)

    # load in correct config file and initialize boto dynamo table
    with open(config_location, "r") as file:
        CONFIG = json.loads(file.read())

    RESERVATION_TABLE = DynamoDBClient(CONFIG["dynamodb"]["reservations"])


def list_reservations():
    LOGGER.info("get_reservation")
    scan = RESERVATION_TABLE.scan("reservations_local")
    print(scan)
    return {
        "statusCode": 200,
        "body": {
            "message": "Get Reservation",
            "data": scan["Items"]
        }
    }


def get_reservation(event):
    LOGGER.info("get_reservation")
    return {
        "statusCode": 200,
        "body": {
            "message": "Get Reservation"
        }
    }


def create_reservation(event):
    j_event = json.loads(event)

    # validate incoming reservation
    assert validate_reservation(j_event["body"])

    # create reservation
    LOGGER.info("create_reservation")

    RESERVATION_TABLE.write(j_event["body"])
    return {
        "statusCode": 200,
        "body": {
            "message": "Create Reservation"
        }
    }


def update_reservation(body):
    LOGGER.info("update_reservation")
    return {
        "statusCode": 200,
        "body": {
            "message": "Update Reservation"
        }
    }


def delete_reservation(body):
    LOGGER.info("delete_reservation")
    return {
        "statusCode": 200,
        "body": {
            "message": "Delete Reservation"
        }
    }


def validate_reservation(reservation):
    return True