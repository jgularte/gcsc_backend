"""
filename: user_info_service.py
author: Jack Gularte
date: March 27 21
"""
# standard imports
import boto3
import json
import logging
import fastjsonschema
from typing import Dict, List
from fastjsonschema.exceptions import JsonSchemaException

# chalice imports
from chalice import Response

# internal imports
from chalicelib.aws_clients import dynamodb_client as dc

# # load in schema file and compile it for quicker evaluations; remember that working dir starts at chalicelib.
# with open("chalicelib/schemas/reservation.json", "r") as schema_file:
#     RES_SCHEMA = json.load(schema_file)
#     COMPILED_SCHEMA = fastjsonschema.compile(RES_SCHEMA)

# logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# globals
TABLE_NAME = ""
HASH_NAME = "user_guid"


def init_service(env_config: Dict) -> None:
    """
    Function used to initiate the service based on the current run env. Set the table info and if we are
    in a local environment, then replace the dynamodb resource in the client with a specialized local endpoint instance.
    :param env_config: The current environment configuration
    :return: None
    """
    global TABLE_NAME
    TABLE_NAME = env_config["user_info_table"]

    if env_config["env"] == "local":
        dc.dynamodb = boto3.resource("dynamodb", endpoint_url=env_config["ddb_endpoint_url"])


def get_userinfo(user_guid: str) -> Response:
    """
    Get a user's profile data via its id.

    :param user_guid: The user's cognito guid
    :return: Chalice response object.
    """
    userinfo = dc.match_primary(
        table_name=TABLE_NAME,
        primary_key=HASH_NAME,
        primary_key_val=user_guid,
        index_name=None,
        query_index=False
    )["Items"]

    # return a 404 if no userinfo found
    if not len(userinfo):
        return Response(
            status_code=404,
            body={
                "error": f"No userinfo with user_guid of '{user_guid}' found."
            }
        )

    # log an error if this reservation guid has multiple entries. Protections in the create/update functions should
    # protect against this though.
    if len(userinfo) > 1:
        logger.error(f"The user_guid '{user_guid}' has {len(userinfo)} profiles in the table.")

    # extract the first profile and convert the profile from Decimals to ints
    user = userinfo[0]
    # convert_reservation_ints(reservation)
    return Response(
        status_code=200,
        body={
            "message": "User profile retrieved.",
            "data": user
        }
    )
