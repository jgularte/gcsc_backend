"""
filename: cognito_client.py
author: Jack Gularte
date: Feb 28 2021
"""

# standard imports
import boto3
import json
import logging
from typing import Dict

# chalice imports
from chalice import Response

cognito = boto3.client("cognito-idp")
AUTH_FLOW = "USER_PASSWORD_AUTH"


def init_auth_flow(client_id: str, username_hash: str, password_hash: str) -> Dict:
    return cognito.initiate_auth(
        AuthFlow=AUTH_FLOW,
        AuthParameters={
            "USERNAME": username_hash,
            "PASSWORD": password_hash
        },
        ClientId=client_id
    )


def respond(client_id: str, session: str, challenge: str, challenge_params: Dict) -> Dict:
    if challenge == "NEW_PASSWORD_REQUIRED":
        assert "NEW_PASSWORD" in challenge_params

    return cognito.respond_to_auth_challenge(
        ClientId=client_id,
        Session=session,
        ChallengeName=challenge,
        ChallengeResponses=challenge_params
    )