"""
filename: reservations_service.py
author: Jack Gularte
date: Nov 25 2020
"""
# standard imports
import boto3
import json
import logging
import fastjsonschema
from typing import Dict, List
from fastjsonschema.exceptions import JsonSchemaException
from uuid import uuid4

# chalice imports
from chalice import Response

# internal imports
from chalicelib.aws_clients import dynamodb_client as dc

# load in schema file and compile it for quicker evaluations; remember that working dir starts at chalicelib.
with open("chalicelib/schemas/reservation.json", "r") as schema_file:
    RES_SCHEMA = json.load(schema_file)
    COMPILED_SCHEMA = fastjsonschema.compile(RES_SCHEMA)

# logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# globals
RES_TABLE = ""
RES_HASH = "reservation_guid"
RES_SORT = "epoch_start"

INT_FIELDS = [
    "epoch_start",
    "epoch_end"
]


def init_service(env_config: Dict) -> None:
    """
    Function used to initiate the service based on the current run env. Set the table info and if we are
    in a local environment, then replace the dynamodb resource in the client with a specialized local endpoint instance.
    :param env_config: The current environment configuration
    :return: None
    """
    global RES_TABLE
    RES_TABLE = env_config["reservations_table"]

    if env_config["env"] == "local":
        dc.dynamodb = boto3.resource("dynamodb", endpoint_url=env_config["ddb_endpoint_url"])


"""
LIST/GET/QUERY
"""


def list_reservations() -> Response:
    """
    List all reservations.
    TODO THIS CAN BE MUCH BETTER
    :return: Chalice response object.
    """
    print(dc.scan_table(table_name=RES_TABLE)["Items"])
    return Response(
        status_code=200,
        body={
            "message": "List successful",
            "data": dc.scan_table(table_name=RES_TABLE)["Items"]
        }
    )


def get_reservation(reservation_guid: str) -> Response:
    """
    Get a reservation via its id.

    :param reservation_guid: The reservation guid
    :return: Chalice response object.
    """
    reservations = dc.match_primary(
        table_name=RES_TABLE,
        primary_key=RES_HASH,
        primary_key_val=reservation_guid,
        index_name=None,
        query_index=False
    )["Items"]

    # return a 404 if no reservation found
    if not len(reservations):
        return Response(
            status_code=404,
            body={
                "error": f"No reservation with reservation_guid of '{reservation_guid}' found."
            }
        )

    # log an error if this reservation guid has multiple entries. Protections in the create/update functions should
    # protect against this though.
    if len(reservations) > 1:
        logger.error(f"The reservation_guid '{reservation_guid}' has {len(reservations)} profiles in the table.")

    # extract the first profile and convert the profile from Decimals to ints
    reservation = reservations[0]
    convert_reservation_ints(reservation)
    return Response(
        status_code=200,
        body={
            "message": "Reservation retrieved.",
            "data": reservation
        }
    )


"""
CREATE/UPDATE
"""


def create_reservation(reservation: dict) -> Response:
    """
    Create a new reservation.

    :param reservation: reservation object to create.
    :return: Chalice response object.
    """
    # give the incoming reservation a guid, if a guid is passed by the user it will override it.
    reservation[RES_HASH] = str(uuid4())

    # first check to see if reservation guid already exists in table. In this case a 404 result is desired.
    # chances are there won't be any conflict since uuid4 guids are 36 chars long but, if a conflict occurs, make sure
    # to handle it
    get_response = get_reservation(
        reservation_guid=reservation[RES_HASH]
    )
    while get_response.status_code != 404:
        reservation[RES_HASH] = str(uuid4())
        get_response = get_reservation(
            reservation_guid=reservation[RES_HASH]
        )

    # validate the incoming reservation, if error, return the error before creation
    try:
        COMPILED_SCHEMA(reservation)
    except JsonSchemaException as jse:
        return Response(
            status_code=400,
            body={
                "error": jse.message
            }
        )

    # write reservation to table
    dc.write(
        table_name=RES_TABLE,
        item=reservation,
        return_values="NONE"
    )

    # return success message.
    return Response(
        status_code=200,
        body={
            "message": "Reservation created.",
            "data": reservation
        }
    )


def update_reservation(reservation: dict) -> Response:
    """
    Update an existing reservation.

    :param reservation: reservation to update.
    :return: Chalice response object.
    """

    # check to make sure that a reservation with this guid exists
    get_response = get_reservation(
        reservation_guid=reservation[RES_HASH]
    )
    if get_response.status_code != 200:
        return Response(
            status_code=400,
            body={
                "error": f"No reservation profile with guid '{reservation[RES_HASH]}' exists. "
                         f"Please create a reservation before updating."
            }
        )

    # validate the incoming reservation, if error, return the error before creation
    try:
        COMPILED_SCHEMA(reservation)
    except JsonSchemaException as jse:
        return Response(
            status_code=400,
            body={
                "error": jse.message
            }
        )

    # write item to table
    dc.write(
        table_name=RES_TABLE,
        item=reservation,
        return_values="NONE"
    )

    # return success message.
    return Response(
        status_code=200,
        body={
            "message": "Reservation updated.",
            "data": reservation
        }
    )


"""
DELETE
"""


def delete_reservation(reservation_guid: str) -> Response:
    """
    Delete a reservation via its guid.

    :param reservation_guid: The reservation guid
    :return: Chalice response object.
    """

    # first get reservation using primary key 'reservation_guid'. If no reservation found return 404 error.
    reservation_resp = get_reservation(
        reservation_guid=reservation_guid
    )
    if reservation_resp.status_code == 404:
        return reservation_resp

    # extract reservation
    reservation = reservation_resp.body["data"]

    dc.delete_item(
        table_name=RES_TABLE,
        item={
            RES_HASH: reservation[RES_HASH],
            RES_SORT: reservation[RES_SORT]
        }
    )
    return Response(
        status_code=200,
        body={
            "message": "Reservation deleted.",
            "data": reservation_guid
        }
    )


"""
HELPERS
"""


def convert_reservation_ints(reservation: dict) -> None:
    """
    Using the global INT_FIELDS list, convert the correct fields from Decimal to int before returning to user.

    :param reservation: The reservation profile returned from dynamodb
    :return: None
    """
    for field in INT_FIELDS:
        reservation[field] = int(reservation[field])
