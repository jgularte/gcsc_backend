"""
filename: reservations_service.py
author: Jack Gularte
date: Nov 25 2020
"""

# chalice imports
from chalice import Response

# internal imports
from .aws_clients import dynamodb_client as dc

# global schemas
# todo these are different for now, once implementation starts determine if they can just be one obj.
CREATE_SCHEMA = {}
UPDATE_SCHEMA = {}


"""
LIST/GET/QUERY
"""


def list_reservations(table_name: str) -> Response:
    """
    List all reservations.

    :param table_name: Table name to search
    :return: Chalice response object.
    """
    return Response(
        status_code=200,
        body={
            "message": "List successful",
            "data": table_name
        }
    )


def get_reservation(table_name: str, reservation_guid: str) -> Response:
    """
    Get a reservation via its id.

    :param table_name: Table name to search
    :param reservation_guid: The reservation guid
    :return: Chalice response object.
    """

    return Response(
        status_code=200,
        body={
            "message": "Reservation retrieved.",
            "data": reservation_guid
        }
    )


"""
CREATE/UPDATE
"""


def create_reservation(table_name: str, reservation: dict) -> Response:
    """
    Create a new reservation.

    :param table_name: Table name to search
    :param reservation: reservation object to create.
    :return: Chalice response object.
    """

    # validate the incoming reservation, if error, return the error before creation
    validated = validate_reservation(reservation, CREATE_SCHEMA)
    if validated.status_code != 200:
        return validated

    # return success message.
    return Response(
        status_code=200,
        body={
            "message": "Reservation created.",
            "data": reservation
        }
    )


def update_reservation(table_name: str, reservation: dict) -> Response:
    """
    Update an existing reservation.

    :param table_name: Table name to search
    :param reservation: reservation to update.
    :return: Chalice response object.
    """

    # validate the incoming reservation, if error, return the error before creation
    validated = validate_reservation(reservation, UPDATE_SCHEMA)
    if validated.status_code != 200:
        return validated

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


def delete_reservation(table_name: str, reservation_guid: str) -> Response:
    """
    Delete a reservation via its guid.

    :param table_name: Table name to search
    :param reservation_guid: The reservation guid
    :return: Chalice response object.
    """
    return Response(
        status_code=200,
        body={
            "message": "Reservation deleted.",
            "data": reservation_guid
        }
    )


"""
VALIDATE
"""


def validate_reservation(reservation: dict, schema: dict) -> Response:
    """
    Using the fastjsonschema package, validate the incoming reservation before creation.

    :param reservation: The reservation object to validate
    :param schema: Schema to validate the object against
    :return: Chalice response object.
    """
    return Response(
        status_code=200,
        body={
            "message": "Reservation validated.",
            "data": None
        }
    )
