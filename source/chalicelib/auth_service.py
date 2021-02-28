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

# chalice imports
from chalice import Response

# local imports
from source.chalicelib.aws_clients import cognito_client

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
AUTH FLOW
"""


def init_auth_flow(client_id: str, username_hash: str, password_hash: str) -> Response:
    resp = cognito_client.init_auth_flow(
        client_id=client_id,
        username_hash=username_hash,
        password_hash=password_hash
    )
    # todo chalice-ize response
    return resp


def respond_auth_flow(client_id: str, challenge: str, session: str, challenge_params: Dict) -> Response:
    if challenge == "NEW_PASSWORD_REQUIRED":
        assert "NEW_PASSWORD" in challenge_params

    resp = cognito_client.respond(
        client_id=client_id,
        challenge=challenge,
        session=session,
        challenge_params=challenge_params
    )
    return resp


def change_password(previous: str, proposed: str, token: str) -> Response:
    pass