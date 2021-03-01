"""
filename: auth_service.py
author: Jack Gularte
date: Feb 28 2021
"""
# standard imports
import boto3
import json
import logging
from typing import Dict, List
from uuid import uuid4
from botocore.exceptions import ClientError
# chalice imports
from chalice import Response

# local imports
from chalicelib.aws_clients import cognito_client

# logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# globals
cc = None


"""
HELPERS
"""


def init_service(env_config: Dict) -> None:
    """
    Function used to initiate the service based on the current run env.
    :param env_config: The current environment configuration
    :return: None
    """
    global cc
    if env_config["env"] == "local":
        pass


"""
ADMIN
"""


def admin_create_user(user_pool_id: str, username: str, temp_password: str, attributes: List[Dict]) -> Dict:
    resp = cognito_client.admin_create_user(
        user_pool_id=user_pool_id,
        temp_password=temp_password,
        username=username,
        attributes=attributes
    )
    return resp


"""
AUTH FLOW
"""


def init_auth_flow(client_id: str, username: str, password_hash: str) -> Response:
    try:
        resp = cognito_client.init_auth_flow(client_id=client_id, username=username, password_hash=password_hash)
    except ClientError as ce:
        logger.error(f"BOTO3 ERROR: {ce.response}")
        return Response(
            status_code=401,
            body={
                "error": "Unauthorized. Invalid "
            }
        )
    # todo chalice-ize response
    return resp


def respond_auth_flow(client_id: str, challenge: str, session: str, challenge_params: Dict) -> Response:
    if challenge == "NEW_PASSWORD_REQUIRED":
        assert "NEW_PASSWORD" in challenge_params

    resp = cognito_client.respond_to_auth_challenge(
        client_id=client_id,
        challenge=challenge,
        session=session,
        challenge_params=challenge_params
    )
    return resp


def change_password(previous: str, proposed: str, token: str) -> Response:
    pass